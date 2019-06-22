from PyQt5.QtCore import *
import requests as req
from bs4 import BeautifulSoup
import os
import time
import re
import urllib.parse as urlparse


class Worker(QObject):
    finished = pyqtSignal(str)
    finished_err = pyqtSignal(list)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

        self.search_link = []

    @pyqtSlot()
    def naverPost(self, url, sprt, path, status):
        try:
            res = req.get(url, headers=self._header)
            naverSoup = BeautifulSoup(res.text, "html.parser")
        except:
            self.finished_err.emit(['4', '0', '', '로드 실패', url])
            QThread.msleep(1300)
            return

        if naverSoup.find("meta", {"property": "og:title"}) is None:
            self.finished_err.emit(['4', '0', '', '로드 실패', url])
            QThread.msleep(1300)
            return

        na_title = '[Naver Post] ' + naverSoup.find("title").text
        na_title = na_title.replace(': 네이버 포스트', '').strip()
        na_title = re.sub("[/\\:*?\"<>|.]", "_", na_title) # Remove special characters from folder name
        na_title = re.sub("\n", "_", na_title) # Remove line feed character from folder name

        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        # I have referred to the code at following address: https://github.com/tucuprum/jjal_downloader
        # Thanks to tucuprum
        soupClass = naverSoup.find("div", {"class", "__viewer_container"})
        soupScript = BeautifulSoup(soupClass.script.string, "html.parser")
        img_tag = soupScript.find_all('img')

        for i in range(0, len(img_tag)):
            img_url = re.sub('\?type=\S+$', '', img_tag[i].get('data-src'))
            img_name = urlparse.unquote(img_url.split('/')[-1])

            self.finished.emit('다운로드 중 (%s): %s' % (status, img_name))

            if sprt:
                if not os.path.isdir('%s%s' % (path, na_title)):
                    try:
                        os.makedirs('%s%s' % (path, na_title))
                    except Exception as E:
                        self.finished_err.emit(['2', E])
                        return

                try:
                    with open('%s%s\\%s' % (path, na_title, img_name), "wb") as file:
                        img = req.get(img_url, headers=self._header)
                        file.write(img.content)
                        file.close()
                    self.finished_err.emit(['4', '1', img_name, '성공', img_url])
                except Exception as E:
                    file.close()
                    print('download image \n %s' % str(E))
                    self.finished_err.emit(['4', '1', img_name, '실패', img_url])
                    return
            else:
                try:
                    with open('%s%s' % (path, img_name), "wb") as file:
                        img = req.get(img_url, headers=self._header)
                        file.write(img.content)
                        file.close()
                    self.finished_err.emit(['4', '1', img_name, '성공', img_url])
                except Exception as E:
                    file.close()
                    print('download image \n %s' % str(E))
                    self.finished_err.emit(['4', '1', img_name, '실패', img_url])
                    return

            QThread.msleep(500)

        self.finished_err.emit(['4', '0', na_title, '', url])
        QThread.msleep(1300)

    @pyqtSlot()
    def topstarnews(self, url, sprt, path, status):
        try:
            res = req.get(url, headers=self._header)
            topstarSoup = BeautifulSoup(res.text, "html.parser")
        except:
            self.finished_err.emit(['4', '0', '', '로드 실패', url])
            QThread.msleep(1300)
            return

        if topstarSoup.find("meta", {"property": "og:title"}) is None:
            self.finished_err.emit(['4', '0', '', '로드 실패', url])
            QThread.msleep(1300)
            return
        
        top_title = '[Topstarnews] ' + topstarSoup.find("meta", {"property": "og:title"}).get("content").strip()
        top_title = top_title = re.sub("[/\\:*?\"<>|.]", "_", top_title)
        top_title = re.sub("\n", "_", top_title)

        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        img_tag = topstarSoup.find("div", {"class": "user-content"}).find_all('img')

        for i in range(0, len(img_tag)):
            img_url = img_tag[i].get('src')
            if img_url is None: # No image tag
                continue

            img_url = 'http://www.topstarnews.net' + img_url
            img_name = urlparse.unquote(img_url.split('/')[-1])
            if img_name[-4:] == '.jpg':
                img_url = 'http://www.topstarnews.net' + img_tag[i].get('data-org')
                img_name = urlparse.unquote(img_url.split('/')[-1])
            elif not img_name[-4:] == '.gif':
                continue

            self.finished.emit('다운로드 중 (%s): %s' % (status, img_name))

            if sprt:
                if not os.path.isdir('%s%s' % (path, top_title)):
                    try:
                        os.makedirs('%s%s' % (path, top_title))
                    except Exception as E:
                        self.finished_err.emit(['2', E])
                        return

                try:
                    with open('%s%s\\%s' % (path, top_title, img_name), "wb") as file:
                        img = req.get(img_url, headers=self._header)
                        file.write(img.content)
                        file.close()
                    self.finished_err.emit(['4', '1', img_name, '성공', img_url])
                except Exception as E:
                    file.close()
                    print('download image \n %s' % str(E))
                    self.finished_err.emit(['4', '1', img_name, '실패', img_url])
                    return
            else:
                try:
                    with open('%s%s' % (path, img_name), "wb") as file:
                        img = req.get(img_url, headers=self._header)
                        file.write(img.content)
                        file.close()
                    self.finished_err.emit(['4', '1', img_name, '성공', img_url])
                except Exception as E:
                    file.close()
                    print('download image \n %s' % str(E))
                    self.finished_err.emit(['4', '1', img_name, '실패', img_url])
                    return

            QThread.msleep(500)

        self.finished_err.emit(['4', '0', top_title, '', url])
        QThread.msleep(1300)


        
    @pyqtSlot()
    def tistory(self, url, sprt, path, status):
        try:
            res = req.get(url, headers=self._header)
            tistorySoup = BeautifulSoup(res.text, "html.parser")
        except:
            self.finished_err.emit(['4', '0', '', '로드 실패', url])
            QThread.msleep(1300)
            return

        if tistorySoup.find("meta", {"property": "og:title"}) is None:
            self.finished_err.emit(['4', '0', '', '로드 실패', url])
            QThread.msleep(1300)
            return

        ti_title = '[Tistory] ' + tistorySoup.find("meta", {"property": "og:title"}).get("content").strip()
        ti_title = re.sub("[/\\:*?\"<>|.]", "_", ti_title) # Remove special characters from folder name
        ti_title = re.sub("\n", "_", ti_title) # Remove line feed character from folder name

        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        img_tag = tistorySoup.find_all('img')
        
        for i in range(0, len(img_tag)):
            img_url = img_tag[i].get('src')
            if re.match("https://t1.daumcdn.net/cfile", img_url): # Old domain (t1.daumcdn.net)
                img_name = img_tag[i].get('filename')
                if img_name is None:
                    img_name = urlparse.unquote(img_url.split('/')[-1]) + '.jpg' # Can't judge wheather the image is jpg, png or gif. So just save as a jpg file.

                img_url += '?original'

            elif re.match("https://k.kakaocdn.net/dn", img_url): # New domain (k.kakaocdn.net)
                img_name = img_tag[i].get('data-filename')
                if img_name is None:
                    img_name = urlparse.unquote(img_url.split('/')[-2]) + '_' + urlparse.unquote(img_url.split('/')[-1])
            else:
                continue                
                
            img_name = re.sub("[/\\:*?\"<>|]", "_", img_name)
            self.finished.emit('다운로드 중 (%s): %s' % (status, img_name))
            
            if sprt:
                if not os.path.isdir('%s%s' % (path, ti_title)):
                    try:
                        os.makedirs('%s%s' % (path, ti_title))
                    except Exception as E:
                        self.finished_err.emit(['2', E])
                        return

                try:
                    with open('%s%s\\%s' % (path, ti_title, img_name), "wb") as file:
                        img = req.get(img_url, headers=self._header)
                        file.write(img.content)
                        file.close()
                    self.finished_err.emit(['4', '1', img_name, '성공', img_url])
                except Exception as E:
                    file.close()
                    print('download image \n %s' % str(E))
                    self.finished_err.emit(['4', '1', img_name, '실패', img_url])
                    return
            else:
                try:
                    with open('%s%s' % (path, img_name), "wb") as file:
                        img = req.get(img_url, headers=self._header)
                        file.write(img.content)
                        file.close()
                    self.finished_err.emit(['4', '1', img_name, '성공', img_url])
                except Exception as E:
                    file.close()
                    print('download image \n %s' % str(E))
                    self.finished_err.emit(['4', '1', img_name, '실패', img_url])
                    return

            QThread.msleep(500)

        self.finished_err.emit(['4', '0', ti_title, '', url])
        QThread.msleep(1300)

    @pyqtSlot(list)
    def main(self, list_):
        self.finished.emit('다운로드 작업을 시작합니다.')

        QThread.msleep(1000)

        self.search_link = list_[0].split('\n')

        for i in range(0, len(self.search_link)):
            if 'post.naver.com' in self.search_link[i]: # Naver Post
                self.naverPost(self.search_link[i], list_[1], list_[2], '%s/%s' % (i + 1, len(self.search_link)))
            elif 'topstarnews.net' in self.search_link[i]: # Topstarnews
                self.topstarnews(self.search_link[i], list_[1], list_[2], '%s/%s' % (i + 1, len(self.search_link)))
            else: # Tistory or Unknown URL
                self.tistory(self.search_link[i], list_[1], list_[2], '%s/%s' % (i + 1, len(self.search_link)))

            QThread.msleep(1000)

        self.finished.emit('다운로드 작업을 완료하였습니다.')
