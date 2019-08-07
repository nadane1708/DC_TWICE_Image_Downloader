from PyQt5.QtCore import *
import requests as req
from bs4 import BeautifulSoup
import os
import time
import re
import json
from lxml import html
import urllib.parse as urlparse


class Worker(QObject):
    finished = pyqtSignal(str)
    finished_err = pyqtSignal(list)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }

    @pyqtSlot()
    def sns_allDownload(self, user, sprt, path): # Download whole contents of Instagram User Page
        try:
            self.finished.emit('해당 ID의 계정을 확인 중 입니다.')
            res = req.get('https://www.instagram.com/' + user + '/?__a=1', headers=self._header)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return

        if res.status_code != 200: # Wrong url or Can't load the page of url
            self.finished_err.emit(['1', '검색하신 페이지를 확인할 수 없습니다.', '해당 주소를 확인하고 다시 시도해주시기 바랍니다.'])
            return

        res = res.json()

        if res['graphql']['user']['is_private']:
            self.finished_err.emit(['1', '검색하신 계정은 비공계 계정입니다.', '다른 계정으로 다시 시도해주시기 바랍니다.'])
            return

        self.finished.emit('페이지에서 쿼리 정보를 로드 중입니다.')
        # I have referred to the code at following address: https://github.com/sachin-bisht/Instagram_Stalker_Scraper
        # Thanks to sachin-bisht
        page = req.get('https://www.instagram.com/' + user + '/')
        data = html.fromstring(page.content)
        link = data.xpath("//head/link[@rel = 'preload']/@href")
        page = req.get('https://www.instagram.com' + link[-1], headers=self._header).text # ProfilePageContainer.js
        ind = page.find('queryId')
        ind += 9
        ind = page.find('queryId', ind)
        ind += 9
        ind = page.find('queryId', ind)
        ind += 9
        st_ind = ind
        lst_ind = page.find('"', ind)

        query_id = page[st_ind:lst_ind]
        user_id = res['graphql']['user']['id']
        url_list = dict()
        query_hash = ''
        graph = ''
        next_page = ''

        self.finished.emit('해당 계정의 글을 불러옵니다. (%s)' % len(url_list))
        try:
            while(True):
                if not graph:
                    query_hash = res['graphql']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

                hash_url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables={"id":"%s","first":12,"after":"%s"}' % (query_id, user_id, query_hash)
                graph = req.get(hash_url, headers=self._header)

                graph = graph.json()


                for i in graph['data']['user']['edge_owner_to_timeline_media']['edges']:
                    if i['node']['__typename'] == 'GraphImage':
                        url_list[user + '_' + i['node']['shortcode']] = [i['node']['display_resources'][len(i['node']['display_resources']) - 1]['src']]
                    elif i['node']['__typename'] == 'GraphVideo':
                        url_list[user + '_' + i['node']['shortcode']] = [i['node']['video_url']]
                    elif i['node']['__typename'] == 'GraphSidecar':
                        sidecarList = list()
                        for j in i['node']['edge_sidecar_to_children']['edges']:
                            if j['node']['__typename'] == 'GraphImage':
                                sidecarList.append(j['node']['display_resources'][len(j['node']['display_resources']) - 1]['src'])
                            elif j['node']['__typename'] == 'GraphVideo':
                                sidecarList.append(j['node']['video_url'])
                        url_list[user + '_' + i['node']['shortcode']] = sidecarList

                self.finished.emit('해당 계정의 게시물을 불러옵니다. (%s)' % len(url_list))
                next_page = graph['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
                if not next_page:
                    break

                query_hash = graph['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

                QThread.msleep(50)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return


        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        index = 1
        for i, j in url_list.items():
            for k in j:
                img_name = urlparse.unquote(k.split('/')[-1])
                img_name = re.sub('[?]_nc_ht.*', '', img_name)

                self.finished.emit('다운로드 중 (%s/%s): %s' % (index, len(url_list), img_name))

                if sprt:
                    if not os.path.isdir('%s%s' % (path, i)):
                        try:
                            os.makedirs('%s%s' % (path, i))
                        except Exception as E:
                            self.finished_err.emit(['2', E])
                            return

                    try:
                        with open('%s%s\\%s' % (path, i, img_name), "wb") as file:
                            img = req.get(k, headers=self._header)
                            file.write(img.content)
                            file.close()
                            
                            if img_name[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        self.finished_err.emit(['2', E])
                        return
                else:
                    try:
                        with open('%s%s' % (path, img_name), "wb") as file:
                            img = req.get(k, headers=self._header)
                            file.write(img.content)
                            file.close()

                            if img_name[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        self.finished_err.emit(['2', E])
                        return

                QThread.msleep(500)
                index += 1

            QThread.msleep(700)

    @pyqtSlot()
    def sns_segDownload(self, url, sprt, path, status): # Download contents of Instagram Page
        try:
            if url.split('/')[-3] != 'p':
                url = url + '/'
            res = req.get(url + '?__a=1', headers=self._header)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return

        if res.status_code != 200: # Wrong url or Can't load the page of url
            self.finished_err.emit(['1', '검색하신 페이지를 확인할 수 없습니다.', '해당 주소를 확인하고 다시 시도해주시기 바랍니다.'])
            return

        res = res.json()

        url_list = dict()

        if res['graphql']['shortcode_media']['__typename'] == 'GraphImage': # Only 1 image
            url_list[res['graphql']['shortcode_media']['owner']['username'] + '_' + res['graphql']['shortcode_media']['shortcode']] = [res['graphql']['shortcode_media']['display_resources'][len(res['graphql']['shortcode_media']['display_resources']) - 1]['src']]
        elif res['graphql']['shortcode_media']['__typename'] == 'GraphVideo': # Only 1 video
            url_list[res['graphql']['shortcode_media']['owner']['username'] + '_' + res['graphql']['shortcode_media']['shortcode']] = [res['graphql']['shortcode_media']['video_url']]
        elif res['graphql']['shortcode_media']['__typename'] == 'GraphSidecar':
            sidecarList = list()
            for i in res['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
                if i['node']['__typename'] == 'GraphImage':
                    sidecarList.append(i['node']['display_resources'][len(i['node']['display_resources']) - 1]['src'])
                elif i['node']['__typename'] == 'GraphVideo':
                    sidecarList.append(i['node']['video_url'])
            url_list[res['graphql']['shortcode_media']['owner']['username'] + '_' + res['graphql']['shortcode_media']['shortcode']] = sidecarList

        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        for i, j in url_list.items():
            for k in j:
                img_name = urlparse.unquote(k.split('/')[-1])
                img_name = re.sub('[?]_nc_ht.*', '', img_name)

                self.finished.emit('다운로드 중 (%s): %s' % (status, img_name))

                if sprt:
                    if not os.path.isdir('%s%s' % (path, i)):
                        try:
                            os.makedirs('%s%s' % (path, i))
                        except Exception as E:
                            self.finished_err.emit(['2', E])
                            return

                    try:
                        with open('%s%s\\%s' % (path, i, img_name), "wb") as file:
                            img = req.get(k, headers=self._header)
                            file.write(img.content)
                            file.close()
                            
                            if img_name[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        self.finished_err.emit(['2', E])
                        return
                else:
                    try:
                        with open('%s%s' % (path, img_name), "wb") as file:
                            img = req.get(k, headers=self._header)
                            file.write(img.content)
                            file.close()

                            if img_name[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        self.finished_err.emit(['2', E])
                        return

                QThread.msleep(500)

            QThread.msleep(700)

    @pyqtSlot(list)
    def main(self, list_):
        self.finished.emit('다운로드 작업을 시작합니다.')

        QThread.msleep(1000)

        if list_[0] == 1:
            self.sns_allDownload(list_[1], list_[2], list_[3])
        elif list_[0] == 2:
            search_link = []
            search_link = list_[1].split('\n')

            for i in range(0, len(search_link)):
                self.sns_segDownload(search_link[i], list_[2], list_[3], '%s/%s' % (i + 1, len(search_link)))

                QThread.msleep(1000)

        self.finished.emit('다운로드 작업을 완료하였습니다.')