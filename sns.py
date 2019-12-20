from PyQt5.QtCore import *
import requests as req
from bs4 import BeautifulSoup
import os
import time
import re
import json
from lxml import html
import urllib.parse as urlparse


# Instagram Download
class Worker(QObject):
    finished = pyqtSignal(str)
    finished_err = pyqtSignal(list)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }

    @pyqtSlot()
    def inst_allDownload(self, user, sprt, path): # Download whole contents of Instagram User Page
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

    @pyqtSlot(list)
    def main(self, list_):
        self.finished.emit('다운로드 작업을 시작합니다.')
        QThread.msleep(1000)

        self.inst_allDownload(list_[0], list_[1], list_[2])

        self.finished.emit('다운로드 작업을 완료하였습니다.')


# Twitter Download
class Worker_2(QObject):
    finished = pyqtSignal(str)
    finished_err = pyqtSignal(list)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        self._video_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA' 
        }

    # I have referred to the code at following address: https://github.com/dc-koromo/koromo-copy/blob/master/Koromo_Copy.Framework/Extractor/TwitterExtractor.cs
    # Thanks to koromo
    @pyqtSlot()
    def tw_allDownload(self, user, retwt, sprt, path):
        media_list = []

        try:
            self.finished.emit('해당 ID의 계정을 확인 중 입니다.')
            res = req.get('https://twitter.com/%s' % user, headers=self._header)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return

        docs = html.fromstring(res.content)
        try:
            min_pos = docs.xpath('//*[@id="timeline"]/div/@data-min-position')[0]
        except Exception as E:
            if 'out of range' in str(E):
                self.finished_err.emit(['1', '검색하신 페이지를 확인할 수 없습니다.', '해당 주소를 확인하고 다시 시도해주시기 바랍니다.'])
                return
            else:
                self.finished_err.emit(['2', E])
                return

        tweets = docs.xpath("//*/li[@data-item-type='tweet']")
        if tweets == []:
            self.finished_err.emit(['1', '검색하신 페이지를 확인할 수 없습니다.', '해당 주소를 확인하고 다시 시도해주시기 바랍니다.'])
            return

        self.finished.emit('해당 계정의 글을 불러옵니다. (%s)' % len(media_list))

        # First page
        for i in tweets:
            parse_list = []
            tweet_user = i.xpath(".//div[1]/@data-screen-name")[0]
            tweet_id = i.xpath(".//div[1]/@data-tweet-id")[0]
            has_img = i.xpath(".//*[@class='AdaptiveMedia-container']//img/@src")
            has_video = i.xpath(".//*[@class='AdaptiveMediaOuterContainer']//div[@class='AdaptiveMedia-video']")

            if not retwt:
                if not user == tweet_user:
                    continue

            if has_img:
                parse_list.append(tweet_user)
                parse_list.append(tweet_id)
                parse_list.append(has_img)
            elif has_video:
                parse_list.append(tweet_user)
                parse_list.append(tweet_id)

                try:
                    video_json = req.get('https://api.twitter.com/1.1/statuses/show.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&trim_user=false&include_ext_media_color=true&id=%s' % tweet_id, headers=self._video_header)
                except Exception as E:
                    self.finished_err.emit(['2', E])
                    return
                video_json = video_json.json()
                variants = video_json['extended_entities']['media'][0]['video_info']['variants']
                if isinstance(variants, list):
                    for i in variants:
                        if 'mp4' in i['content_type']:
                            parse_list.append(i['url'])
                            break
                else:
                    parse_list.append(variants[0]['url'])

                QThread.msleep(1000)

            if not parse_list == []:
                media_list.append(parse_list)

            self.finished.emit('해당 계정의 글을 불러옵니다. (%s)' % len(media_list))

        # Loop for pages after first. Second page, Third page, and so on.
        while(True):
            if retwt:
                api_url = 'https://twitter.com/i/profiles/show/%s/timeline/tweets?include_available_features=1&include_entities=1&max_position=%s&reset_error_state=false' % (user, min_pos)
            else:
                api_url = 'https://twitter.com/i/profiles/show/%s/media_timeline?include_available_features=1&include_entities=1&max_position=%s&reset_error_state=false' % (user, min_pos)

            try:
                api_json = req.get(api_url, headers=self._header).json()
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

            min_pos = api_json['min_position']
            docs = html.fromstring(api_json['items_html'])
            tweets = docs.xpath("//*/li[@data-item-type='tweet']")

            if tweets == []:
                print('None tweets array')
                break

            for i in tweets:
                parse_list = []
                tweet_user = i.xpath(".//div[1]/@data-screen-name")[0]
                tweet_id = i.xpath(".//div[1]/@data-tweet-id")[0]
                has_img = i.xpath(".//*[@class='AdaptiveMediaOuterContainer']//img/@src")
                has_video = i.xpath(".//*[@class='AdaptiveMediaOuterContainer']//div[@class='AdaptiveMedia-video']")

                if has_img: # multiple images
                    parse_list.append(tweet_user)
                    parse_list.append(tweet_id)
                    parse_list.append(has_img)    
                elif has_video:
                    parse_list.append(tweet_user)
                    parse_list.append(tweet_id)

                    try:
                        video_json = req.get('https://api.twitter.com/1.1/statuses/show.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&trim_user=false&include_ext_media_color=true&id=%s' % tweet_id, headers=self._video_header)
                        video_json = video_json.json()
                    except Exception as E:
                        self.finished_err.emit(['2', E])
                        return

                    variants = video_json['extended_entities']['media'][0]['video_info']['variants']
                    if isinstance(variants, list):
                        for i in variants:
                            if 'mp4' in i['content_type']:
                                parse_list.append(i['url'])
                                break
                    else:
                        parse_list.append(variants[0]['url'])

                    QThread.msleep(500)

                if not parse_list == []:
                    media_list.append(parse_list)

                self.finished.emit('해당 계정의 글을 불러옵니다. (%s)' % len(media_list))
                QThread.msleep(500)

            if not api_json['has_more_items']:
                print('no more')
                break

        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        index = 1
        for i in media_list:
            if sprt:
                if not os.path.isdir('%s%s' % (path, i[0] + '_' + i[1])):
                    try:
                        os.makedirs('%s%s' % (path, i[0] + '_' + i[1]))
                    except Exception as E:
                        print(str(E))
                        return

                if isinstance(i[2], list):
                    for j in i[2]:
                        self.finished.emit('다운로드 중 (%s/%s): %s' % (index, len(media_list), re.sub("\?tag=\d+", "", j.split('/')[-1])))
                        try:
                            with open('%s%s\\%s' % (path, i[0] + '_' + i[1], re.sub("\?tag=\d+", "", j.split('/')[-1])), "wb") as file:
                                img = req.get(j + ':orig', headers=self._header)
                                file.write(img.content)
                                file.close()

                                if re.sub("\?tag=\d+", "", j.split('/')[-1])[-4:] == '.jpg':
                                    self.finished_err.emit(['5', img.content])
                        except Exception as E:
                            file.close()
                            print(str(E))
                            return
                else:
                    self.finished.emit('다운로드 중 (%s/%s): %s' % (index, len(media_list), re.sub("\?tag=\d+", "", i[2].split('/')[-1])))
                    try:
                        with open('%s%s\\%s' % (path, i[0] + '_' + i[1], re.sub("\?tag=\d+", "", i[2].split('/')[-1])), "wb") as file:
                            img = req.get(i[2] + ':orig', headers=self._header)
                            file.write(img.content)
                            file.close()

                            if re.sub("\?tag=\d+", "", i[2].split('/')[-1])[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        print(str(E))
                        return
            else:
                if isinstance(i[2], list):
                    for j in i[2]:
                        self.finished.emit('다운로드 중 (%s/%s): %s' % (index, len(media_list), re.sub("\?tag=\d+", "", j.split('/')[-1])))
                        try:
                            with open('%s%s' % (path, re.sub("\?tag=\d+", "", j.split('/')[-1])), "wb") as file:
                                img = req.get(j + ':orig', headers=self._header)
                                file.write(img.content)
                                file.close()

                                if re.sub("\?tag=\d+", "", j.split('/')[-1])[-4:] == '.jpg':
                                    self.finished_err.emit(['5', img.content])
                        except Exception as E:
                            file.close()
                            print(str(E))
                            return
                else:
                    self.finished.emit('다운로드 중 (%s/%s): %s' % (index, len(media_list), re.sub("\?tag=\d+", "", i[2].split('/')[-1])))
                    try:
                        with open('%s%s' % (path, re.sub("\?tag=\d+", "", i[2].split('/')[-1])), "wb") as file:
                            img = req.get(i[2] + ':orig', headers=self._header)
                            file.write(img.content)
                            file.close()

                            if re.sub("\?tag=\d+", "", i[2].split('/')[-1])[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        print(str(E))
                        return

            index += 1

    @pyqtSlot(list)
    def main(self, list_):
        self.finished.emit('다운로드 작업을 시작합니다.')

        QThread.msleep(1000)

        self.tw_allDownload(list_[0], list_[1], list_[2], list_[3])

        self.finished.emit('다운로드 작업을 완료하였습니다.')


# Instagram / Twitter Download Partially
class Worker_3(QObject):
    finished = pyqtSignal(str)
    finished_err = pyqtSignal(list)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self._header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        self._video_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA' 
        }

    @pyqtSlot()
    def inst_segDownload(self, url, sprt, path, status): # Download contents of Instagram Page
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

    @pyqtSlot()
    def tw_segDownload(self, url, sprt, path, status):
        try:
            res = req.get(url, headers=self._header)
        except Exception as E:
            self.finished_err.emit(['2', E])
            return

        docs = html.fromstring(res.content)
        try:
            tweet_html = docs.xpath(".//*[@class='permalink-inner permalink-tweet-container']")[0]
        except Exception as E:
            if 'out of range' in str(E):
                self.finished_err.emit(['1', '검색하신 페이지를 확인할 수 없습니다.', '해당 주소를 확인하고 다시 시도해주시기 바랍니다.'])
                return
            else:
                self.finished_err.emit(['2', E])
                return

        tweet_user = tweet_html.xpath(".//div[1]/@data-screen-name")[0]
        tweet_id = tweet_html.xpath(".//div[1]/@data-tweet-id")[0]
        has_img = tweet_html.xpath(".//*[@class='AdaptiveMedia-container']//img/@src")
        has_video = tweet_html.xpath(".//*[@class='AdaptiveMediaOuterContainer']//div[@class='AdaptiveMedia-video']")

        if has_img:
            src = has_img
        elif has_video:
            src = []

            try:
                video_json = req.get('https://api.twitter.com/1.1/statuses/show.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&trim_user=false&include_ext_media_color=true&id=%s' % tweet_id, headers=self._video_header)
                video_json = video_json.json()
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

            variants = video_json['extended_entities']['media'][0]['video_info']['variants']
            if isinstance(variants, list):
                for i in variants:
                    if 'mp4' in i['content_type']:
                        src.append(i['url'])
                        break
            else:
                src.append(variants[0]['url'])

        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as E:
                self.finished_err.emit(['2', E])
                return

        if sprt:
            if not os.path.isdir('%s%s' % (path, tweet_user + '_' + tweet_id)):
                try:
                    os.makedirs('%s%s' % (path, tweet_user + '_' + tweet_id))
                except Exception as E:
                    print(str(E))
                    return

            if isinstance(src, list):
                for i in src:
                    self.finished.emit('다운로드 중 (%s): %s' % (status, re.sub("\?tag=\d+", "", i.split('/')[-1])))
                    try:
                        with open('%s%s\\%s' % (path, tweet_user + '_' + tweet_id, re.sub("\?tag=\d+", "", i.split('/')[-1])), "wb") as file:
                            img = req.get(i + ':orig', headers=self._header)
                            file.write(img.content)
                            file.close()

                            if re.sub("\?tag=\d+", "", i.split('/')[-1])[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        print(str(E))
                        return
            else:
                self.finished.emit('다운로드 중 (%s): %s' % (status, re.sub("\?tag=\d+", "", src.split('/')[-1])))
                try:
                    with open('%s%s\\%s' % (path, tweet_user + '_' + tweet_id, re.sub("\?tag=\d+", "", src.split('/')[-1])), "wb") as file:
                        img = req.get(src + ':orig', headers=self._header)
                        file.write(img.content)
                        file.close()

                        if re.sub("\?tag=\d+", "", src.split('/')[-1])[-4:] == '.jpg':
                            self.finished_err.emit(['5', img.content])
                except Exception as E:
                    file.close()
                    print(str(E))
                    return
        else:
            if isinstance(src, list):
                for i in src:
                    self.finished.emit('다운로드 중 (%s): %s' % (status, re.sub("\?tag=\d+", "", i.split('/')[-1])))
                    try:
                        with open('%s%s' % (path, re.sub("\?tag=\d+", "", i.split('/')[-1])), "wb") as file:
                            img = req.get(i + ':orig', headers=self._header)
                            file.write(img.content)
                            file.close()

                            if re.sub("\?tag=\d+", "", i.split('/')[-1])[-4:] == '.jpg':
                                self.finished_err.emit(['5', img.content])
                    except Exception as E:
                        file.close()
                        print(str(E))
                        return
            else:
                self.finished.emit('다운로드 중 (%s): %s' % (status, re.sub("\?tag=\d+", "", src.split('/')[-1])))
                try:
                    with open('%s%s' % (path, re.sub("\?tag=\d+", "", src.split('/')[-1])), "wb") as file:
                        img = req.get(src + ':orig', headers=self._header)
                        file.write(img.content)
                        file.close()

                        if re.sub("\?tag=\d+", "", src.split('/')[-1])[-4:] == '.jpg':
                            self.finished_err.emit(['5', img.content])
                except Exception as E:
                    file.close()
                    print(str(E))
                    return

    @pyqtSlot(list)
    def main(self, list_):
        self.finished.emit('다운로드 작업을 시작합니다.')
        QThread.msleep(1000)

        search_link = []
        search_link = list_[0].split('\n')

        for i in range(0, len(search_link)):
            if 'instagram.com' in search_link[i]:
                self.inst_segDownload(search_link[i], list_[1], list_[2], '%s/%s' % (i + 1, len(search_link)))
            elif 'twitter.com' in search_link[i]:
                self.tw_segDownload(search_link[i], list_[1], list_[2], '%s/%s' % (i + 1, len(search_link)))

        self.finished.emit('다운로드 작업을 완료하였습니다.')
