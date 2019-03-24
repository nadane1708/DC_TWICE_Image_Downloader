from PyQt5.QtCore import *
import requests as req
from bs4 import BeautifulSoup
import os
import time


class Worker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self._major_url = 'https://gall.dcinside.com/board/lists/?id='
        self._minor_url = 'https://gall.dcinside.com/mgallery/board/lists?id='
        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Host': 'gall.dcinside.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }

        self._gall_id = ['twice', 'twicetv', 'nayeone', 'jungyeon', 'momo', 'sanarang', 'jihyo', 'twicemina', 'dahyeon', 'sonchaeyoung', 'tzuyu0614']

        self._init_subject = []
        self._init_link = []
        self._init_number = []
        self._search_subject = []
        self._search_link = []
        self._search_number = []

        self._except_subject = []
        self._except_link = []
        self._except_number = []

    # Check if the gallery is major or minor
    @pyqtSlot()
    def check_gall(self, idx):
        res = req.get('%s%s' % (self._major_url, self._gall_id[idx]), headers=self._header)
        gallSoup = BeautifulSoup(res.text, "html.parser")
        meta_data = gallSoup.find_all("meta", {"name": "title"})

        # Minor gallery
        if not meta_data:
            return False

        # Major gallery
        return True

    # Get html from gallery page & Make link and subject lists
    @pyqtSlot()
    def get_page(self, url, page, rcmd):
        res = req.get(('%s&page=%s%s' % (url, page, '&exception_mode=recommend') if rcmd else '%s&page=%s' % (url, page)), headers=self._header)
        pageSoup = BeautifulSoup(res.text, "html.parser")
        data = pageSoup.find_all("td", {"class": "gall_tit ub-word"})

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

    # Get html from gallery post & Make link and file name lists
    @pyqtSlot()
    def get_image(self, sprt, drtry):
        for i in range(0, len(self._search_subject)):
            res = req.get('https://gall.dcinside.com%s' % self._search_link[i], headers=self._header)
            postSoup = BeautifulSoup(res.text, "html.parser")
            img_data = postSoup.find("ul", {"class": "appending_file"}).find_all("a")

            for j in img_data:
                if sprt:
                    self.download_image(j.get("href"), j.text, drtry, '[%s] %s' % (self._search_number[i], self._search_subject[i]))
                else:
                    self.download_image(j.get("href"), j.text, drtry)

    # Download images from posts to directory
    @pyqtSlot()
    def download_image(self, url, filename, directory, subject=''):
        print('Download: %s' % filename)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        if subject:
            if not os.path.isdir('%s%s' % (directory, subject)):
                os.makedirs('%s%s' % (directory, subject))
            with open('%s%s\\%s' % (directory, subject, filename), "wb") as file:
                img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._header)
                file.write(img.content)
                file.close()
        else:
            with open('%s%s' % (directory, filename), "wb") as file:
                img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._header)
                file.write(img.content)
                file.close()

        # Sleep for avoiding traffic block; Change value as you wish.
        time.sleep(0.3)
        
    # Main function
    @pyqtSlot()
    def main(self, idx, search, page, by, rcmd, excpt, sprt, drtry):
        self.finished.emit('다운로드를 시작합니다.')
        is_major = self.check_gall(idx)
        url = '%s%s' % ((self._major_url if is_major else self._minor_url), self._gall_id[idx])

        self.finished.emit('갤러리 체크 완료')
        
        page = page.replace(" ", "") # Replace " " (space) to "" (null)
        page_number = page.split(",")

        for i in page_number:
            if '-' in i:
                for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                    self.get_page(url, j, rcmd)
            else:
                self.get_page(url, i, rcmd)

        print('search filter')
        # Filter subjects including search words and "by" word
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

        print('Remove except word')
        # Remove elements including except keywords from lists
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

        print(len(self._search_subject))
        for i in self._search_subject:
            print(i)

        print('get post')
        self.get_image(sprt, drtry)


if __name__ == '__main__':
    session = dc()
    session.main(2, 'gif','20 - 30', 1, 1, '', 0, 'C:\\Users\\Sean\\Desktop\\TWICE 이미지 다운로더\\test')