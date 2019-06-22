# DC_TWICE_Image_Downloader
Image Downloader for DCinside TWICE gallery.

디시인사이드 TWICE 갤러리 짤 다운로더

# Caution
본 프로그램은 Python 3.6.8 & PyQt5 으로 작성되었으며, 프로그램 사용에 의해 발생하는 모든 책임은 사용자 본인에게 있습니다.

# Description
TWICE 갤러리 짤 다운로더는 디시인사이드 [TWICE 갤러리](https://gall.dcinside.com/board/lists/?id=twice)와 멤버 갤러리([나](https://gall.dcinside.com/board/lists/?id=nayeone)[정](https://gall.dcinside.com/mgallery/board/lists/?id=jungyeon)[모](https://gall.dcinside.com/mgallery/board/lists/?id=momo)[사](https://gall.dcinside.com/board/lists/?id=sanarang)[지](https://gall.dcinside.com/mgallery/board/lists/?id=jihyo)[미](https://gall.dcinside.com/mgallery/board/lists/?id=twicemina)[다](https://gall.dcinside.com/board/lists/?id=dahyeon)[채](https://gall.dcinside.com/mgallery/board/lists/?id=sonchaeyoung)[쯔](https://gall.dcinside.com/mgallery/board/lists/?id=tzuyu0614)), [TWICE TV 마이너 갤러리](https://gall.dcinside.com/mgallery/board/lists/?id=twicetv), 그리고 [스트리밍 마이너 갤러리](https://gall.dcinside.com/mgallery/board/lists/?id=streaming) 에서 이미지를 다운받는 프로그램입니다.  
또한 해당 갤러리의 ID를 이용하여 이미지를 검색하기 때문에 앞서 언급한 갤러리 이외의 갤러리에서도 다운로드가 가능합니다.

### 프로그램 설명
#### 갤러리 id  
* 검색하고자 하는 갤러리의 id를 입력합니다. 콤보박스를 내려 갤러리 선택이 가능합니다.
  
#### 페이지  
* 검색하고자 하는 페이지를 입력합니다. 페이지는 데스크톱 페이지 기준이며, 쉼표(",")와 붙임표("-")를 사용하여 여러 페이지 설정이 가능합니다.  
예를 들어 1페이지에서 10페이지까지 검색하고자 한다면 "1-10"을 입력하며, 1페이지와 5페이지를 검색하고자 한다면 "1,5"을 입력합니다.

#### 검색어  
* 검색하고자 하는 단어를 입력합니다. 쉼표를 사용하여 여러 단어를 설정할 수 있습니다.  
예를 들어 "gif"와 "움짤"을 검색하고자 한다면 "gif,움짤"을 입력합니다.  
* ".by만 받기" 체크 박스를 체크하여 검색어에 기본으로 "by"를 추가할 수 있으며, "개념글" 체크 박스를 체크하여 개념글 페이지를 기준으로 검색할 수 있습니다.

#### 제외 단어  
* 검색할 때 제외하고자 하는 단어를 입력합니다. 검색어와 마찬가지로 쉼표를 사용하여 여러 단어를 설정할 수 있습니다.  
* "프리뷰 제외" 체크 박스를 체크하여 제외 단어에 기본으로 "프리뷰"를 추가할 수 있습니다.

#### 폴더 경로  
* 다운로드한 이미지를 저장하고자 하는 폴더를 선택합니다. "..." 버튼을 눌러 경로 다이얼로그 창을 열어 편리하게 경로 지정이 가능합니다. 단, 직접 입력할 경우 반드시 폴더명 뒤에 백슬래시("\\")를 입력하시기 바랍니다.  
예를 들어 저장 경로가 C드라이브의 "image" 폴더인 경우 "C:\image\\"를 입력하시기 바랍니다.  
* "사진별 폴더에 저장" 체크 박스를 체크하여 이미지를 검색된 글 제목 폴더별로 이미지 저장이 가능합니다. 이 경우 폴더명 맨 앞에 해당 글의 번호가 추가 됩니다. 체크 박스를 체크 해제 했을 경우 지정한 경로 폴더 한 곳에 모아서 저장이 되며 이 경우 파일명 맨 앞에 해당 글의 번호가 추가 됩니다.

#### 다운로드  
* 다운로드 버튼을 눌러 이미지 다운로드 작업을 시작합니다.

#### 취소  
* 취소 버튼을 눌러 이미지 다운로드 작업을 중지합니다.

#### 다운로드 트리뷰 위젯  
* 다운로드 진행상황 표시 트리뷰 위젯입니다. 게시물의 이미지 다운로드 실패나 게시물 내용 로딩 실패 등이 표시됩니다.

#### 재다운로드  
* 재다운로드 버튼을 눌러 다운로드를 실패한 목록의 이미지 재다운로드 작업을 시작합니다.

#### 선택 삭제  
* 트리뷰 위젯에서 복수 선택한 목록을 삭제합니다.

#### 목록 초기화  
* 트리뷰 위젯의 모든 목록을 삭제합니다.

#### 다운로드 할 주소  
이미지를 다운로드 받을 네이버 포스트나 티스토리 주소, 톱스타뉴스 주소를 한 줄에 한 개씩 적습니다.

# Release
* [v1.0](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.0) - 2019/04/15  
첫번째 릴리즈

* [v1.01](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.01) - 2019/04/16  
폴더명 특수문자 오류 수정

* v1.1 - 2019/04/20  
예외 처리 및 예외 발생 메시지 추가  
콤보박스 목록에 스트리밍 마이너 갤러리 추가  
마이너 버그 수정  

* [v1.1a](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.1a) - 2019/04/21  
마이너 갤러리에서 검색이 안되던 점 수정  

* [v1.2](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.2) - 2019/05/04  
갤러리 모든 페이지 다운로드 기능 추가  
콤보박스 목록 선택 버그 수정  
트래픽 부하 방지 대기시간 조절  
필터링 누락 문제 수정  
프리셋 자동 저장/불러오기 기능 추가  
32비트 환경 호환성 문제 해결  

* [v1.21](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.21) - 2019/05/07  
오래된 글에서의 폴더명 생성 오류 수정  
제외 단어 설정 오류 수정  
제외 단어에 공백 문자가 붙는 점 수정  

* [v1.3](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.3) - 2019/05/30  
다운로드 진행 상황 트리뷰 위젯 추가  
예외 처리 코드 수정  
필터링 중복 실행 버그 수정  
재다운로드, 선택 삭제, 목록 초기화 버튼 추가  

* [v1.4](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.4) - 2019/06/09  
네이버 포스트, 티스토리 원본 저장 기능 추가  
재다운로드 강제 종료 버그 수정  
디시 갤러리 페이지 분석 버그 수정  
파일 저장 관련 코드 안정화  

* [v1.41](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.41) - 2019/06/17  
톱스타뉴스 원본 저장 기능 추가  
티스토리  관련 버그 수정  

* [v1.42](https://github.com/nadane1708/DC_TWICE_Image_Downloader/releases/tag/v1.42) - 2019/06/23  
특정 티스토리 페이지에서의 다운로드 오류 수정    

# Contact
본 TWICE 갤러리 짤 다운로더와 관련 문의사항은 아래 오픈카톡 주소로 연락바랍니다.  
https://open.kakao.com/o/sfmnlrpb  

# Thanks to
[트갤차트봇](https://gall.dcinside.com/board/view?id=twice&no=3939753) - Inspired by his/her program  
[Zard](https://gallog.dcinside.com/blueaqua1019) (DC TWICE Gallery) - Beta Tester & Feedback  
[별*](https://gallog.dcinside.com/acalffkstlqkf) (DC TWICE Gallery) - Feedback

# License
GNU General Public License v3.0
