
#  *SKN24-4th-5Team* 
> 대주제 :  AI 활용 애플리케이션 개발
> 세부 주제 : LLM을 연동한 내외부 문서 기반 질의 응답 웹페이지 개발
> 일정 : 2020~~~~~


##  **1.  팀 소개**

## 팀명 : Waypoint

**유학의 시작부터 출국까지, 가장 확실한 두 가지 관문을 연결하는 안내자** 

-  **Waypoint**는 유학생들이 반드시 거쳐야 하는 두 지점, **입시 정보 탐색**과 **비자 인터뷰 합격**에서 사용자가 길을 잃지 않도록 정확한 가이드를 제공하는 기술적 거점(Waypoint)이 되고자 합니다.

##  팀원 소개

<br>

| 박정은 | 정재훈 | 조아름 | 권민세 | 
| :---: | :---: | :---: | :---: |
|  <a href="https://github.com/brainkat"><img src="https://img.shields.io/badge/brainkat-181717?style=for-the-badge&logo=github&logoColor=white"/></a> | <a href="https://github.com/JeaHoon-J"><img src="https://img.shields.io/badge/JeaHoon--J-181717?style=for-the-badge&logo=github&logoColor=white"/></a> | <a href="https://github.com/areum117"><img src="https://img.shields.io/badge/areum117-181717?style=for-the-badge&logo=github&logoColor=white"/></a> |<a href="https://github.com/KweonMinSe0109"><img src="https://img.shields.io/badge/KweonMinSe0109-181717?style=for-the-badge&logo=github&logoColor=white"/></a> |
</br>
<br>

# **Contents**

1.  [팀 소개](#1--팀-소개)
2.  [프로젝트 개요](#2-️-프로젝트-개요)
3.  [기술 스택](#3-️-기술-스택)
4.  [시스템 구성도](#5-시스템-아키텍처)
5.  [요구사항 명세서](#7-요구사항-명세서)
6.  [화면설계서](#7-요구사항-명세서)
7.  [WBS](#6-️-wbs)
8.  [테스트 계획&결과 보고서](#10--테스트-계획-및-결과-보고서)
9.  [수행결과](#12--수행결과)
10.  [진행과정 중 프로그램 개선 노력](#11-진행과정-중-프로그램-개선-노력)
11.  [한 줄 회고](#13--한-줄-회고)
</br>



##  **2.  프로젝트 개요**

##  **2.1 프로젝트 명 : `Viva la Vista`**

로고 넣기
  
>  **“Viva la Vista!”** : 스페인어 '인생이여 만세(Viva la Vida)'에서 착안하여, **'성공적인 유학을 통해 펼쳐질 당신의 찬란한 앞날(Vista) 만세!'**라는 의미함

`비자 성공부터 글로벌 입시까지 아자아자!! ୧(⑅˃ᗜ˂⑅)୨ 응원합니다!`


##  **2.2 프로젝트 소개**

<br> **전 세계 대학 입시 정보 챗봇**과 **AI 비자 인터뷰 시뮬레이션** 서비스 제공

- **Viva la Vista**는유학 준비생들이 마주하는 가장 큰 두 가지 거대 장벽을 허물기 위해 **전 세계 대학 입시 정보 챗봇**과 **AI 비자 인터뷰 시뮬레이션** 서비스를 제공함
</br>


## **2.3 프로젝트 배경 및 필요성**

###  **<h3> 1. 성인 학위 유학 중심으로의 시장 재편** </h3>
- 통계청 『유학생 현황』에 따르면, 2010년대 후반 들어 이러한 초·중·고교생의 조기유학수요가 크게 감소하였고 전체 유학 시장에서 성인층 위주의 유학 수요로 재편됨 
	- 👉 **학위 과정 비중의 압도적 증가:** 2023년 기준 해외 유학생의 약 79%가 정규 학위 취득을 목적으로 체류 중이며, 이는 단순 경험보다 '확실한 결과'를 원하는 고관여 사용자가 늘어났음을 의미합니다.

![조기유학 감소](https://edumorning.com/storage/uploads/q2qOWQ3NH623rdJTcy8YRC2HQdWcrvOBjlO0TPaX.jpg)

사진1(메인) / 사진 2(유학생 원그래프) 
https://edumorning.com/articles/1029

###  **<h3> 2. 미국 유학의 견고한 수요와 높아지는 진입 장벽** </h3>
*   고환율, 자국민 우선주의, 취업 불안정성 등 현실적인 리스크가 그 어느 때보다 심화되었지만, 미국은 여전히 압도적인 유학생 비중 1위를 기록하며 견고한 선호도를 보이고 있습니다.
    *   👉 복잡해진 상황 속에서 사용자가 궁금한 점을 즉시 해소하고 **검증된 입시 데이터에 24시간 접근할 수 있는 챗봇 서비스**가 필요함

![유학생 통계](https://cdn.topdigital.com.au/news/photo/202604/30560_50951_250.jpg)
https://www.topdigital.com.au/news/articleView.html?idxno=30560


###  **<h3> 3. 학생비자 거부율 35%, 10년 내 최고치,  “미국 유학 장벽 현실화”** </h3>
*   트럼프 행정부 심사 강화 여파로 국제교육업체 쇼어라이트(Shorelight) 분석 결과 2025년 F-1(유학생) 비자 거부율은 35%로 집계됐다. 이는 2024년 31%에서 상승한 수치로, 2015년 이후 10년간 가장 높은 수준인 것을 확인 할 수 있음 👉 실제 영사와의 인터뷰 환경을 완벽히 재현하여 사용자에게 실질적인 대비책 필요함


https://knewsla.com/usa/20260415110110/
https://www.vietnam.vn/ko/ty-le-truot-visa-du-hoc-my-cao-nhat-10-nam
https://www.vietnam.vn/ko/ty-le-truot-visa-du-hoc-uc-cao-nhat-trong-hai-thap-nien
![Tỷ lệ trượt visa du học Mỹ cao nhất 10 năm - Ảnh 1.](https://vstatic.vietnam.vn/vietnam/resource/IMAGE/2026/04/16/1776333309240_ty-le-tu-choi-visa-du-hoc-my-2025-177630997872062448217.jpeg)

###  **<h3> 4. 실용적 유학 트렌드와 대안 탐색 확대** </h3>

*   단순히 '타이틀'을 쫓던 과거와 달리, 예산 내에서 실리를 찾는 '실용 유학'과 미국 외 대안 국가의 대학교를 찾는 수요가 늘고 있습니다.
    *   👉 수십 개의 유학원에 파편화된 정보를 일일이 대조하는 대신,  **24시간 입시 상담**으로 최적의 대안 학교를 발굴하고, **AI 인터뷰 시뮬레이션**을 통해 35%의 거절 리스크를 극복하는 데이터 기반의 올인원(All-in-one) 솔루션이 필요함
    
https://www.naeil.com/news/read/556332?ref=naver

![](https://wimg.naeil.com/paper/2025/07/30/20250730_01100118000001_L01.jpg)

</br>

##  **2.4 프로젝트 목표**

### **[Vista 1] Broad Perspective: 넓은 시야**

-   **서비스:** 글로벌 입시 정보 통합 검색 챗봇
    
-   **가치:** 특정 국가나 학교에 국한되지 않고, 사용자의 조건에 맞는 전 세계(일본, 유럽, 호주 등) 대안 대학을 즉각 탐색하여 최적의 선택지를 제공합니다.
    

### **[Vista 2] Clear Vision: 명확한 전망**

-   **서비스:** AI 비자 인터뷰 시뮬레이션
    
-   **가치:** 35%에 달하는 비자 거절 불확실성을 정면으로 돌파합니다. 실제 인터뷰 데이터를 기반으로 한 반복 훈련과 피드백을 통해 합격이라는 명확한 결과를 설계합니다.
    

### **[Viva!] Encouragement: 당신의 도전을 향한 찬사**

-   **가치:** 복잡한 절차와 정보 불균형 속에서 유학 준비생이 겪는 심리적 피로를 혁신적인 UX로 해소합니다. 리스크를 줄이고 성공적인 시작을 할 수 있도록 기술로 응원합니다.
  
  

##  3. 🛠️ 기술 스택

| 분류 | 기술 및 도구 |
| :---: | :--- |
| **Web Frontend** | ![](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |
| **Backend** | ![](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) |
| **LLM** | ![](https://img.shields.io/badge/LangChain-00C7B7?style=for-the-badge&logoColor=white) ![](https://img.shields.io/badge/LangGraph-FF6F00?style=for-the-badge&logoColor=white) ![](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white) ![](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white) |
| **Cloud & Infra** | ![](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white) ![](https://img.shields.io/badge/EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white) ![](https://img.shields.io/badge/RunPod-7B42BC?style=for-the-badge&logoColor=white) ![](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) |
| **Database** | ![](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white) ![](https://img.shields.io/badge/AWS%20RDS-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white) ![](https://img.shields.io/badge/ChromaDB-5A45FF?style=for-the-badge&logoColor=white) |
| **Development** | ![](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white) ![](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white) ![](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) |


##  4. 사용 모델 --> 수정


##  5. 🧩시스템 아키텍처 ##  --> 수정



##  6. 🖼️ WBS  --> 수정
  

##  7. 📝요구사항 명세서  --> 수정

  
##  10. 📻 테스트 계획 및 결과 보고서


##  11. 🔍서비스모델 성능 개선을 위한 노력

  

###  ☑️개선방안: 1. (서비스1: 입시서비스 챗봇) SQL 쿼리 에러 체크 및 재작성 로직 구축

단순히 쿼리를 생성하고 실행하는 단계를 넘어, Self-Correction과정을 도입함으로써 쿼리 에러 체크 로직은 데이터의 정확성 향상

1.  구조적 안정성: check_query와 retry_query 노드를 추가함으로써, 문법 오류나 존재하지 않는 컬럼 참조 등의 에러 발생 시 시스템이 즉시 중단되지 않고 스스로 문제를 해결합니다.

2.  할루시네이션(환각) 방지: get_schema를 통해 실제 데이터베이스 구조를 참조하고, 실행 전 쿼리를 검증함으로써 잘못된 데이터를 사용자에게 제공할 확률을 최소화합니다.

전체 흐름 : START → list_tables → call_get_schema → get_schema → generate_query → check_query → run_query → [성공: generate_answer → END] / [실패: retry_query → run_query]

  

###  ☑️개선방안: 2. (서비스2: 비자인터뷰 챗봇) STT, TTS를 활용한 VISA 인터뷰어 평가 적용

향후 인터뷰를 위해 보다 현실적인 환경을 모방하기 위해 STT와 TTS를 추가했습니다. STT와 TTS는 사용자가 답변 녹음에 대한 평가를 받을 때 평가 프롬프트의 일부였습니다. 녹음을 분석하기 위해 librosa라는 라이브러리를 사용했습니다. librosa 덕분에 모델은 일시 정지, 즉 모델이 인터뷰어를 평가하는 데 사용한 볼륨을 평가할 수 있었습니다.

  
  

###  ☑️개선방안: 3. (멀티에이전트) 통일된 모델을 활용한 루트 노드 생성 후 서비스 분류

루트 노드 분류 : 특정 키워드('학비', '마감' 등)를 즉시 감지하여 **입시 서비스(Service 1)** 로 강제 라우팅 / 인터뷰 흐름이 끊기지 않고 **비자인터뷰 챗봇(Service 2)** 유지

1.  일관된 사용자 경험: 사용자가 인터뷰 도중 갑자기 입시 정보를 물어보거나, 반대로 입시 질문을 하다가 인터뷰를 시작하고 싶어 할 때 유연하게 대응할 수 있습니다.

2.  확장성: 향후 새로운 서비스(예: 장학금 안내, 캠퍼스 투어)가 추가되더라도 루트 노드의 분류 로직에 키워드나 라벨만 추가하면 쉽게 확장 가능합니다.

 
##  12. 💻 수행결과

-  서비스 영상 추가

  

##  13. 한 줄 회고

  

|  **이름**  |  **회고 내용**  |

|  --------  |  -------------  |

| 권민세 |

| 박정은 | |

| 정재훈 |  |

| 조아름 | 
