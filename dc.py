from PyQt5.QtCore import *
import requests as req
from bs4 import BeautifulSoup
import os
import time
import re


class Worker(QObject):
    finished = pyqtSignal(str)
    finished_err = pyqtSignal(list)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self._major_url = 'https://gall.dcinside.com/board/lists/?id='
        self._minor_url = 'https://gall.dcinside.com/mgallery/board/lists?id='
        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Host': 'gall.dcinside.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        }

    # Check if the gallery is major or minor
    @pyqtSlot()
    def check_gall(self, idx):
        res = req.get('%s%s' % (self._major_url, idx), headers=self._header)
        gallSoup = BeautifulSoup(res.text, "html.parser")
        meta_data = gallSoup.find_all("meta", {"name": "title"})

        if not meta_data: # Gallery id error
            is_exist = re.findall('갤러리 접속 에러', res.text)
            if is_exist:
                self.finished_err.emit(['검색하신 갤러리가 존재하지 않습니다.', '갤러리 id를 확인하고 다시 시도해주시기 바랍니다.', ''])
                return -1
            return False # Minor gallery

        # Major gallery
        return True

    # Get html from gallery page & Make link and subject lists
    @pyqtSlot()
    def get_page(self, url, page, rcmd):
        res = req.get(('%s&page=%s%s' % (url, page, '&exception_mode=recommend') if rcmd else '%s&page=%s' % (url, page)), headers=self._header)
        pageSoup = BeautifulSoup(res.text, "html.parser")
        data = pageSoup.find_all("td", {"class": "gall_tit ub-word"})

        try:
            for i in data:
                data_obj = i.find("a")
                if data_obj.find("em").get("class")[1] == 'icon_pic':
                    self._init_subject.append(data_obj.text.strip())
                    self._init_link.append(data_obj.get("href"))
                    self._init_number.append(i.parent.find("td", {"class": "gall_num"}).text)
                elif data_obj.find("em").get("class")[1] == 'icon_recomimg':
                    self._init_subject.append(data_obj.text.strip())
                    self._init_link.append(data_obj.get("href"))
                    self._init_number.append(i.parent.find("td", {"class": "gall_num"}).text)
        except Exception as E:
                self.finished_err.emit(['', '', E])
                return

    # Get html from gallery post & Make link and file name lists
    @pyqtSlot()
    def get_image(self, sprt, drtry):
        for i in range(0, len(self._search_subject)):
            res = req.get('https://gall.dcinside.com%s' % self._search_link[i], headers=self._header)
            postSoup = BeautifulSoup(res.text, "html.parser")
            img_data = postSoup.find("ul", {"class": "appending_file"}).find_all("a")

            try:
                for j in img_data:
                    self.finished.emit('다운로드 중 (%s/%s): %s' % (i + 1, len(self._search_subject), j.text))
                    if sprt:
                        self.download_image(j.get("href"), (j.text if j.text else 'null'), drtry, '[%s] %s' % (self._search_number[i], self._search_subject[i]))
                    else:
                        self.download_image(j.get("href"), '[%s] %s' % (self._search_number[i], (j.text if j.text else 'null')), drtry)
            except Exception as E:
                self.finished_err.emit(['', '', E])
                return

    # Download images from posts to directory
    @pyqtSlot()
    def download_image(self, url, filename, directory, subject=''):
        # print('Download: %s' % filename)

        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except Exception as E:
                self.finished_err.emit(['', '', E])
                return

        if subject:
            subject = re.sub("[/\\:*?\"<>|.]", "_", subject) # Remove special characters from folder name
            if not os.path.isdir('%s%s' % (directory, subject)):
                os.makedirs('%s%s' % (directory, subject))
            try:
                with open('%s%s\\%s' % (directory, subject, filename), "wb") as file:
                    img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._header)
                    file.write(img.content)
                    file.close()
            except Exception as E:
                self.finished_err.emit(['', '', E])
                return
        else:
            try:
                with open('%s%s' % (directory, filename), "wb") as file:
                    img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._header)
                    file.write(img.content)
                    file.close()
            except Exception as E:
                self.finished_err.emit(['', '', E])
                return

        # Sleep for avoiding traffic block; Change value as you wish.
        QThread.sleep(1)
        
    # Main function
    @pyqtSlot(list)
    def main(self, list_):
        
        self._init_subject = []
        self._init_link = []
        self._init_number = []
        self._search_subject = []
        self._search_link = []
        self._search_number = []

        self._except_subject = []
        self._except_link = []
        self._except_number = []

        idx = list_[0]
        search = list_[1]
        page = list_[2]
        by = list_[3]
        rcmd = list_[4]
        excpt = list_[5]
        sprt = list_[6]
        drtry = list_[7]

        self.finished.emit('다운로드 작업을 시작합니다.')
        is_major = self.check_gall(idx)
        if is_major == -1:
            return

        url = '%s%s' % ((self._major_url if is_major else self._minor_url), idx)

        self.finished.emit('갤러리 체크 완료. 키워드 필터링 작업 중입니다.')
        
        p = re.compile("[^0-9-,]")
        if p.search(page):
            self.finished_err.emit(['검색하신 페이지가 존재하지 않습니다.', '페이지 입력란에 숫자(0 ~ 9) 또는 붙임표(-) 외에 문자가 포함되어 있지 않은지 확인하고 다시 시도해주시기 바랍니다.', ''])
            return

        page = page.replace(" ", "") # Replace " " (space) to "" (null)
        page_number = page.split(",")

        for i in page_number:
            if '-' in i:
                for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                    self.get_page(url, j, rcmd)
            else:
                self.get_page(url, i, rcmd)

        # Filter subjects including search words and "by" word
        # print('search filter')
        search_word = search.split(",")
        if search_word:
            for i in search_word:
                for j in range(0, len(self._init_subject)):
                    if i in self._init_subject[j]:
                        if by:
                            if 'by' in self._init_subject[j]:
                                self._search_subject.append(self._init_subject[j])
                                self._search_link.append(self._init_link[j])
                                self._search_number.append(self._init_number[j])
                        
                            continue

                        self._search_subject.append(self._init_subject[j])
                        self._search_link.append(self._init_link[j])
                        self._search_number.append(self._init_number[j])
        else:
            for j in range(0, len(self._init_subject)):
                self._search_subject.append(self._init_subject[j])
                self._search_link.append(self._init_link[j])
                self._search_number.append(self._init_number[j])

        # Remove elements including except keywords from lists
        # print('Remove except word')
        except_word = excpt.split(",")        
        for i in except_word:   
            if i == '':
                continue

            for j in range(0, len(self._search_subject)):
                if i in self._search_subject[j]:
                    self._except_subject.append(self._search_subject[j])
                    self._except_link.append(self._search_link[j])
                    self._except_number.append(self._search_number[j])

        for i in range(0, len(self._except_subject)):
            self._search_subject.remove(self._except_subject[i])
            self._search_link.remove(self._except_link[i])
            self._search_number.remove(self._except_number[i])

        '''
        print(len(self._search_subject))
        for i in self._search_subject:
            print(i)
        '''

        #print('get post')
        self.finished.emit('이미지 다운로드를 시작합니다.')
        self.get_image(sprt, drtry)
        self.finished.emit('다운로드 작업을 완료하였습니다.')

'''
if __name__ == '__main__':
    session = dc()
    session.main(2, 'gif','20 - 30', 1, 1, '', 0, 'C:\\Users\\Sean\\Desktop\\TWICE 이미지 다운로더\\test\\')
'''
