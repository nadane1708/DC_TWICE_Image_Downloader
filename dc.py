from PyQt5.QtCore import *
import requests as req
from bs4 import BeautifulSoup
import os
import time
import re
import platform


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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        self._image_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Host': 'img.dcinside.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Referer': 'https://gall.dcinside.com/'        
        }

    # Check if the gallery is major or minor
    @pyqtSlot()
    def check_gall(self, idx):
        try:
            res = req.get('%s%s' % (self._major_url, idx), headers=self._header)
            gallSoup = BeautifulSoup(res.text, "html.parser")
            meta_data = gallSoup.find_all("meta", {"name": "title"})
            is_exist = re.findall('갤러리 접속 에러', res.text)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return

        if is_exist: # Gallery id error
            self.finished_err.emit(['1', '검색하신 갤러리를 확인할 수 없습니다.', '갤러리 id를 확인하고 다시 시도해주시기 바랍니다.'])
            return -1

        if not meta_data:
            return False # Minor gallery

        # Major gallery
        return True

    # Get the last number of gallery page
    @pyqtSlot()
    def get_final_page(self, url, rcmd):
        try:
            res = req.get('%s%s' % (url, '&exception_mode=recommend') if rcmd else '%s' % url, headers=self._header)
            pageSoup = BeautifulSoup(res.text, "html.parser")
            page_box = pageSoup.find("div", {"class": "bottom_paging_box"}).find_all('a')

            if not page_box:
                self._page_end = 1
                return

            for i in page_box:
                self._page_end = re.search("&page=([0-9]+)", i.get("href")).group(1)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return

    # Get html from gallery page & Make link and subject lists
    @pyqtSlot()
    def get_page(self, url, page, rcmd):
        try:
            res = req.get(('%s&page=%s%s' % (url, page, '&exception_mode=recommend') if rcmd else '%s&page=%s' % (url, page)), headers=self._header)
            pageSoup = BeautifulSoup(res.text, "html.parser")
            data = pageSoup.find_all("td", {"class": "gall_tit ub-word"})

            if self.is_major: # Major gallery
                for i in data:
                    if i.parent.find("td", {"class": "gall_num"}).text == '공지':
                        continue
                    elif i.parent.find("td", {"class": "gall_num"}).text == 'AD':
                        continue
                    elif i.parent.find("td", {"class": "gall_num"}).text == '설문':
                        continue
                    elif i.parent.find("td", {"class": "gall_num"}).text == '이슈':
                        continue

                    data_obj = i.find("a")
                    self._init_title.append(data_obj.text.strip())
                    self._init_link.append(data_obj.get("href"))
                    self._init_number.append(i.parent.find("td", {"class": "gall_num"}).text)
            else:
                if data[0].parent.find("td", {"class": "gall_subject"}): # Minor gallery with subject & title
                    for i in data:
                        if i.parent.find("td", {"class": "gall_subject"}).text == '공지':
                            continue
                        elif i.parent.find("td", {"class": "gall_subject"}).text == 'AD':
                            continue
                        elif i.parent.find("td", {"class": "gall_subject"}).text == '설문':
                            continue
                        elif i.parent.find("td", {"class": "gall_subject"}).text == '이슈':
                            continue

                        data_obj = i.find("a")
                        self._init_title.append(data_obj.text.strip())
                        self._init_link.append(data_obj.get("href"))
                        self._init_number.append(i.parent.find("td", {"class": "gall_num"}).text)
                        self._init_subject.append(i.parent.find("td", {"class": "gall_subject"}).text)
                else: # Minor gallery with title
                    for i in data:
                        if i.parent.find("td", {"class": "gall_num"}).text == '공지':
                            continue
                        elif i.parent.find("td", {"class": "gall_num"}).text == 'AD':
                            continue
                        elif i.parent.find("td", {"class": "gall_num"}).text == '설문':
                            continue
                        elif i.parent.find("td", {"class": "gall_num"}).text == '이슈':
                            continue

                        data_obj = i.find("a")
                        self._init_title.append(data_obj.text.strip())
                        self._init_link.append(data_obj.get("href"))
                        self._init_number.append(i.parent.find("td", {"class": "gall_num"}).text)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return

        self.finished.emit('페이지의 글을 불러옵니다. (%s)' % len(self._init_title))

    # Get html from gallery post & Make link and file name lists
    @pyqtSlot()
    def get_image(self, sprt, drtry):
        for i in range(0, len(self._search_title)):            
            try:
                title = '[%s] %s' % (self._search_number[i], self._search_title[i])
                res = req.get('https://gall.dcinside.com%s' % self._search_link[i], headers=self._header)
                postSoup = BeautifulSoup(res.text, "html.parser")

                if postSoup.find("meta", {"name": "description"}) is None: # The post has deleted or has been failed to load
                    self.finished_err.emit(['3', '0', title, '로드 실패', 'https://gall.dcinside.com%s' % self._search_link[i], ''])
                    QThread.msleep(1300)
                    continue

                post_content = postSoup.find("div", {"class": "writing_view_box"}).text.strip()

                if postSoup.find("ul", {"class": "appending_file"}) is None: # The post has no images
                    self.finished_err.emit(['3', '0', title, '이미지 없음', 'https://gall.dcinside.com%s' % self._search_link[i], post_content])
                    QThread.msleep(1300)
                    continue

                img_data = postSoup.find("ul", {"class": "appending_file"}).find_all("a")

                for j in img_data:
                    self.finished.emit('다운로드 중 (%s/%s): %s' % (i + 1, len(self._search_title), j.text))
                    if sprt:
                        self.download_image(j.get("href"), (j.text if j.text else 'null'), drtry, '[%s] %s' % (self._search_number[i], self._search_title[i]))
                    else:
                        self.download_image(j.get("href"), '[%s] %s' % (self._search_number[i], (j.text if j.text else 'null')), drtry)
                self.finished_err.emit(['3', '0', title, '', 'https://gall.dcinside.com%s' % self._search_link[i], post_content])
            except Exception as E:
                print('get image \n %s' % str(E))
                self.finished_err.emit(['3', '0', title, '로드 실패', 'https://gall.dcinside.com%s' % self._search_link[i], ''])
                QThread.msleep(1300)

    # Download images from posts to directory
    @pyqtSlot()
    def download_image(self, url, filename, directory, title=''):
        # print('Download: %s' % filename)

        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        if title:
            title = re.sub("[/\\:*?\"<>|.]", "_", title) # Remove special characters from folder name
            title = re.sub("\n", "_", title) # Remove line feed character from folder name
            if not os.path.isdir('%s%s' % (directory, title)):
                try:
                    os.makedirs('%s%s' % (directory, title))
                except Exception as E:
                    self.finished_err.emit(['2', E])
                    return
            try:
                if platform.system() == 'Windows':
                    file_dir = '%s%s\\%s' % (directory, title, filename)
                else:
                    file_dir = '%s%s/%s' % (directory, title, filename)
                with open(file_dir, "wb") as file:
                    img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._image_header)
                    file.write(img.content)
                    file.close()
                self.finished_err.emit(['3', '1', filename, '성공', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
            except Exception as E:
                file.close()
                # print('download image \n %s' % str(E))
                self.finished_err.emit(['3', '1', filename, '실패', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
                return
        else:
            try:
                with open('%s%s' % (directory, filename), "wb") as file:
                    img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._image_header)
                    file.write(img.content)
                    file.close()
                self.finished_err.emit(['3', '1', filename, '성공', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
            except Exception as E:
                file.close()
                # print('download image \n %s' % str(E))
                self.finished_err.emit(['3', '1', filename, '실패', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
                return

        # Sleep for avoiding traffic block; Change value as you wish.
        QThread.msleep(1300)

    # Main function
    @pyqtSlot(list)
    def main(self, list_):
        
        self._init_title = []
        self._init_link = []
        self._init_number = []
        self._init_subject = []

        self._search_title = []
        self._search_link = []
        self._search_number = []
        self._search_subject = []

        self._page_end = 0
            
        idx = list_[0]
        search = list_[1]
        page = list_[2]
        by = list_[3]
        rcmd = list_[4]
        hdline = list_[5]
        excpt = list_[6]
        sprt = list_[7]
        drtry = list_[8]

        # self.finished_err.emit(['※ 주의 사항', '한번에 너무 많은 페이지를 다운받게 되면\n트래픽 초과로 디시 서버 접속이 일시적으로\n중단되어 다운로드 작업이 중지 될 수 있습니다.\n이 점 유의 바랍니다.', ''])

        self.finished.emit('다운로드 작업을 시작합니다.')
        self.is_major = self.check_gall(idx)
        if self.is_major == -1:
            return

        url = '%s%s' % ((self._major_url if self.is_major else self._minor_url), idx)

        self.get_final_page(url, rcmd) # Get the final page number for downloading whole pages and for additional purpose in the future

        self.finished.emit('갤러리 체크 완료. 페이지 글 불러오기 작업을 시작합니다.')
        QThread.msleep(1000)

        if not page: # Page input is blank; Download whole pages
            if self._page_end == 1:
                page = '1'
            else:
                page = '1-%s' % self._page_end
        else: # Unexpected input like Alphabet or Hangul
            p = re.compile("[^0-9-,]")
            if p.search(page):
                self.finished_err.emit(['1', '검색하신 페이지가 존재하지 않습니다.', '페이지 입력란에 숫자(0 ~ 9) 또는 붙임표(-) 외에 문자가 포함되어 있지 않은지 확인하고 다시 시도해주시기 바랍니다.'])
                return

        page = page.replace(" ", "") # Replace " " (space) to "" (null)
        page_number = page.split(",")

        for i in page_number:
            if '-' in i:
                for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                    self.get_page(url, j, rcmd)
            else:
                self.get_page(url, i, rcmd)

        self.finished.emit('글 불러오기 작업 완료. 키워드 필터링 작업을 시작합니다.')
        QThread.msleep(1000)

        # Filter subjects including search words and "by" word
        # print('search filter')
        if search or by:
            search_word = search.split(",")
            for i in search_word:
                i = i.strip() # Trim whitespace
                for j in range(0, len(self._init_title)):
                    if i in self._init_title[j]:
                        if by:
                            if 'by' in self._init_title[j]:
                                self._search_title.append(self._init_title[j])
                                self._search_link.append(self._init_link[j])
                                self._search_number.append(self._init_number[j])

                                if hdline and (self.is_major == False):
                                    self._search_subject.append(self._init_subject[j])

                                self.finished.emit('키워드 필터링 작업 중 입니다. (%s)' % len(self._search_title))

                            continue

                        self._search_title.append(self._init_title[j])
                        self._search_link.append(self._init_link[j])
                        self._search_number.append(self._init_number[j])

                        if hdline and (self.is_major == False):
                            self._search_subject.append(self._init_subject[j])

                        self.finished.emit('키워드 필터링 작업 중 입니다. (%s)' % len(self._search_title))
        else:
            for j in range(0, len(self._init_title)):
                self._search_title.append(self._init_title[j])
                self._search_link.append(self._init_link[j])
                self._search_number.append(self._init_number[j])

                if hdline and (self.is_major == False):
                    self._search_subject.append(self._init_subject[j])

                self.finished.emit('키워드 필터링 작업 중 입니다. (%s)' % len(self._search_title))

        # Remove duplicates from filtered lists
        try:
            for i in range(0, len(self._search_number)):
                dupl_list = [ j for j, x in enumerate( self._search_number ) if x == self._search_number[i] ]
                dupl_list.pop(0)
                for j in range(0, len(dupl_list)):
                    self._search_number.pop(dupl_list[j] - j)
                    self._search_title.pop(dupl_list[j] - j)
                    self._search_link.pop(dupl_list[j] - j)

                    if hdline and (self.is_major == False):
                        self._search_subject.pop(dupl_list[j] - j)

        except Exception as e:
            if str(e) == 'list index out of range':
                pass
            else:
                raise

        # Remove elements including except keywords from lists
        # print('Remove except word')
        if excpt:
            except_index = 0
            except_word = excpt.split(",")
            is_exclude = False
            for i in range(0, len(self._search_title)):
                for j in except_word:
                    j = j.strip()
                    if j == '':
                        continue

                    if j in self._search_title[i]:
                        is_exclude = True

                if is_exclude:
                    if hdline and (self.is_major == False):
                        temp_except = [self._search_title[i], self._search_link[i], self._search_number[i], self._search_subject[i]]
                    else:
                        temp_except = [self._search_title[i], self._search_link[i], self._search_number[i]]
                    
                    del self._search_title[i]
                    del self._search_link[i]
                    del self._search_number[i]
                    del self._search_subject[i]

                    self._search_title.insert(0, temp_except[0])
                    self._search_link.insert(0, temp_except[1])
                    self._search_number.insert(0, temp_except[2])

                    if hdline and (self.is_major == False):
                        self._search_subject.insert(0, temp_except[3])

                    except_index += 1

                is_exclude = False

            if except_index:
                del self._search_title[0:except_index]
                del self._search_link[0:except_index]
                del self._search_number[0:except_index]

                if hdline and (self.is_major == False):
                    del self._search_subject[0:except_index]

        # If subject words exist, (Only works on Minor gallery with subject & title)
        # Remove elements that don't include search subject keywords from lists
        if hdline and (self.is_major == False):
            hdline_index = 0
            search_hdline = hdline.split(",")
            is_include = False
            for i in range(0, len(self._search_title)):
                for j in search_hdline:
                    j = j.strip()
                    if j == '':
                        continue

                    if self._search_subject[i] == j:
                        is_include = True

                if not is_include:
                    temp_hdline = [self._search_title[i], self._search_link[i], self._search_number[i], self._search_subject[i]]
                    del self._search_title[i]
                    del self._search_link[i]
                    del self._search_number[i]
                    del self._search_subject[i]

                    self._search_title.insert(0, temp_hdline[0])
                    self._search_link.insert(0, temp_hdline[1])
                    self._search_number.insert(0, temp_hdline[2])
                    self._search_subject.insert(0, temp_hdline[3])

                    hdline_index += 1

                is_include = False

            if hdline_index:
                del self._search_title[0:hdline_index]
                del self._search_link[0:hdline_index]
                del self._search_number[0:hdline_index]
                del self._search_subject[0:hdline_index]

        self.finished.emit('키워드 필터링 작업을 완료했습니다. (%s)' % len(self._search_title))
        QThread.msleep(1000)

        self.finished.emit('다운로드 작업을 시작합니다.')
        QThread.msleep(2000) # Sleep for avoiding traffic block
        self.get_image(sprt, drtry)
        self.finished.emit('다운로드 작업을 완료하였습니다.')

class retryWorker(QObject):
    finished = pyqtSignal(str)
    finished_err = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Host': 'gall.dcinside.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self._image_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Host': 'img.dcinside.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Referer': 'https://gall.dcinside.com/'        
        }

    @pyqtSlot()
    def download_image(self, url, filename, directory, title=''):
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        if title:
            title = re.sub("[/\\:*?\"<>|.]", "_", title) # Remove special characters from folder name
            title = re.sub("\n", "_", title) # Remove line feed character from folder name
            if not os.path.isdir('%s%s' % (directory, title)):
                try:
                    os.makedirs('%s%s' % (directory, title))
                except Exception as E:
                    self.finished_err.emit(['2', E])
                    return
            try:
                if platform.system() == 'Windows':
                    file_dir = '%s%s\\%s' % (directory, title, filename)
                else:
                    file_dir = '%s%s/%s' % (directory, title, filename)
                with open(file_dir, "wb") as file:
                    img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._image_header)
                    file.write(img.content)
                    file.close()
                self.finished_err.emit(['3', '1', filename, '성공', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
            except Exception as E:
                file.close()
                print('download image \n %s' % str(E))
                self.finished_err.emit(['3', '1', filename, '실패', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
                return
        else:
            try:
                with open('%s%s' % (directory, filename), "wb") as file:
                    img = req.get(url.replace('download.php', 'viewimage.php'), headers=self._image_header)
                    file.write(img.content)
                    file.close()
                self.finished_err.emit(['3', '1', filename, '성공', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
            except Exception as E:
                file.close()
                print('download image \n %s' % str(E))
                self.finished_err.emit(['3', '1', filename, '실패', '%s' % url.replace('download.php', 'viewimage.php'), img.content])
                return

        # Sleep for avoiding traffic block; Change value as you wish.
        QThread.msleep(1300)

    @pyqtSlot()
    def retry_download(self, re_list):
        for i in range(0, len(re_list[0])):
            try:
                re_res = req.get('%s' % re_list[0][i][1], headers=self._header)
                re_postSoup = BeautifulSoup(re_res.text, "html.parser")

                if re_postSoup.find("meta", {"name": "description"}) is None: # The post has deleted or has been failed to load
                    self.finished_err.emit(['3', '0', re_list[0][i][0], '로드 실패', '%s' % re_list[0][i][1], ''])
                    QThread.msleep(1300)
                    continue

                re_post_content = re_postSoup.find("div", {"class": "writing_view_box"}).text.strip()

                if re_postSoup.find("ul", {"class": "appending_file"}) is None: # The post has no images
                    self.finished_err.emit(['3', '0', re_list[0][i][0], '이미지 없음', '%s' % re_list[0][i][1], re_post_content])
                    QThread.msleep(1300)
                    continue

                re_img_data = re_postSoup.find("ul", {"class": "appending_file"}).find_all("a")

                for j in re_img_data:
                    self.finished.emit('다운로드 중 (%s/%s): %s' % (i + 1, len(re_list[0]), j.text))
                    if re_list[1]:
                        self.download_image(j.get("href"), (j.text if j.text else 'null'), re_list[2], '%s' % re_list[0][i][0])
                    else:
                        number = re.match("\[(\d+)\]", re_list[0][i][0]).group()
                        self.download_image(j.get("href"), '[%s] %s' % (number, (j.text if j.text else 'null')), re_list[2])
                self.finished_err.emit(['3', '0', re_list[0][i][0], '', '%s' % re_list[0][i][1], re_post_content])
            except Exception as E:
                print(str(E))
                self.finished_err.emit(['3', '0', re_list[0][i][0], '로드 실패', '%s' % re_list[0][i][1], ''])
                QThread.msleep(1300)

        self.finished.emit('재다운로드 작업을 완료하였습니다.')

    @pyqtSlot(list)
    def main(self, _list):
        self.finished.emit('재다운로드 작업을 시작합니다.')
        QThread.msleep(2000)
        self.retry_download(_list)
        self.finished.emit('재다운로드 작업을 완료하였습니다.')
