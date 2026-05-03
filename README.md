
# SKN24-4th-5Team
**대주제**: AI 활용 애플리케이션 개발
**세부 주제**: LLM을 연동한 내외부 문서 기반 질의 응답 웹페이지 개발
**일정**: 2020 ~ 



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

---

##  **2.  프로젝트 개요**

##  **2.1 프로젝트 명 : `Visa La Vista`**
  
>  **“Visa la Vista!”** : 스페인어 '인생이여 만세(Viva La Vida)'에서 착안하여, '성공적인 유학을 통해 펼쳐질 당신의 찬란한 앞날(Vista) 만세!'라는 의미함
`비자 성공부터 글로벌 입시까지 아자아자!! ୧(⑅˃ᗜ˂⑅)୨ 응원합니다!`

<p align="center">
  <img src="https://github.com/user-attachments/assets/27df7eed-77cd-43d0-af65-c969b6b9d465" width="400"/>
</p>


##  **2.2 프로젝트 소개**
 **전 세계 대학 입시 정보 챗봇**과 **AI 비자 인터뷰 시뮬레이션** 서비스 제공

- **Viva La Vista**는 유학 준비생들이 마주하는 가장 큰 두 가지 거대 장벽을 허물기 위해 **전 세계 대학 입시 정보 챗봇**과 **AI 모의 비자 인터뷰** 서비스를 제공함

## **2.3 프로젝트 배경 및 필요성**


###  **<h3> 2.3.1. 학위 취득 중심의 유학 시장 개편** </h3>

-   통계청 『유학생 현황』에 따르면, 2010년대 후반 이후 초·중·고교생의 조기 유학 수요가 크게 감소하고, 전체 유학 시장은 **학위 취득 중심의 수요로 재편**되고 있음
-   2023년 기준 해외 유학생의 약 79%가 **정규 학위 취득**을 목적으로 체류 중이며, 이는 단순 경험보다 **확실한 성과**를 원하는 사용자가 늘어났음을 보여줌

	- 👉 **단순 정보 탐색을 넘어 ‘학위 취득과 비자 승인’이라는 구체적 목표를 가진 성인 유학생**을 핵심 타겟으로 설정함

<p align="center">
  <img src="https://github.com/user-attachments/assets/2965af96-db4f-432d-8918-c7c0a3756076"  width="400"/>
</p>

<p>  
출처 : <a href="https://edumorning.com/articles/1029">https://edumorning.com/articles/1029</a>  
</p>

---
###  **<h3> 2.3.2. 분산된 입시 정보로 인한 탐색의 어려움** </h3>

*   국내 대학(연세대 등)은 '통합자료실'을 통해 모든 입시 정보를 단일 PDF로 제공하는 반면, UIUC를 비롯한 해외 대학은 정보가 여러 웹페이지의 분리 및 500~7000 페이지 분량의 입시요강에 파편화되어 있음
    *   👉 이러한 분산된 구조는 유학원 등 특정 서비스 공급자에게 정보 권력이 독점되는 결과를 초래하며, 학생은 고가의 컨설팅 비용을 지불해야만 하는 구조적 비효율에 직면함
    *   👉 따라서 분산된 입시 데이터를 하나로 통합하고, 복잡한 준비 과정을 일괄적으로 관리해 줄 수 있는 통합 솔루션(챗봇)의 도입이 시급함

<img width='680' src="./assets/news1.png" />
<img width='680' src="./assets/news1-1.png" />

[출처: 데일리안](https://www.dailian.co.kr/news/view/1619827/%EC%B5%9C%EA%B7%BC-%EA%B0%95%ED%99%94%EB%90%98%EB%8A%94-%EB%AF%B8%EA%B5%AD%EB%B9%84%EC%9E%90-%EC%9D%B8%ED%84%B0%EB%B7%B0-%EC%A0%95%EC%B1%85%EA%B3%BC-2026)



---

###  **<h3> 2.3.3. 학생비자 거부율 35%, 10년 내 최고치,  “미국 유학 장벽 현실화”** </h3>

*   높은 환율, 자국민 우선주의, 취업 불안정성 등 현실적인 리스크가 그 어느 때보다 심화되었지만, **미국**은 여전히 **압도적인 유학생 비중 1위**를 기록하며 견고한 선호도를 보이고 있음
  
    *   👉 **유학 시장의 진입 장벽이 높아짐에 따라 단 한 번의 실수가 없는 철저한 준비가 요구**
    
*   트럼프 행정부 비자 인터뷰 심사 강화 여파로 국제교육업체 쇼어라이트(Shorelight) 분석 결과, 2025년 **F-1(유학생) 비자 거부율은 35%로 집계**됐다. 이는 2024년 31%에서 상승한 수치로, 2015년 이후 10년간 가장 높은 수준인 것을 확인 할 수 있음

	*   👉 **실제 영사와의 인터뷰 환경을 완벽히 재현하여 사용자에게 실질적인 대비책 필요**
   
	  

<table align="center">
  <tr>
    <td>
      <img src=https://github.com/user-attachments/assets/d1e1f5ae-f94f-4f51-bf36-7cefe9b08000 width="400"/>
    </td>
    <td>
      <img src=https://github.com/user-attachments/assets/00d4cda1-f71a-4f4b-b812-077d6bfb031c width="400"/>
    </td>
  </tr>
</table>

<p>  
출처 : <a href="https://knewsla.com/usa/20260415110110/">https://knewsla.com/usa/20260415110110/</a>  
</p>
<p>  
출처 : <a href="https://www.vietnam.vn/ko/ty-le-truot-visa-du-hoc-my-cao-nhat-10-nam">https://www.vietnam.vn/ko/ty-le-truot-visa-du-hoc-my-cao-nhat-10-nam</a>  
</p>

---

###  **<h3> 2.3.4. 실용적 유학 트렌드와 대안 탐색 확대** </h3>

*   미국 외 대안 국가의 대학교를 찾는 수요가 늘고 있음
  
    *   👉 **특정 국가나 학교에 편중된 유학원의 영업성 정보가 아닌, 전 세계 대학 데이터를 아우르는 객관적인 플랫폼이 필요함**
    

<table align="center">
  <tr>
    <td>
      <img src="https://cdn.topdigital.com.au/news/photo/202604/30560_50951_250.jpg" width="400"/>
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/41d567b0-392f-4a59-929c-ea1451993e25" width="400"/>
    </td>
  </tr>
</table>

<p>
  출처: <a href="https://www.naeil.com/news/read/556332?ref=naver">https://www.naeil.com/news/read/556332?ref=naver</a>
</p>
<p>
  출처: <a href="https://www.topdigital.com.au/news/articleView.html?idxno=30560">https://www.topdigital.com.au/news/articleView.html?idxno=30560</a>
</p>

---

##  **2.4 프로젝트 목표**

### **[1] Broad Perspective: 넓은 시야**

> **목표:** LLM Tool과 SQL Agent 기술로 내부 데이터의 한계를 넘어 전 세계 입시 정보를 통합함

-   **FastAPI 기반 입시 정보 통합 검색 챗봇**: 주요 대학의 정밀 DB(SQL Agent)와 실시간 외부 탐색 툴(LLM Tool)을 결합하여, 사용자의 조건에 맞는 전 세계 대안 대학 정보를 즉각 제공함
  
    -   **[한계 극복]** 
	    - 고정된 내부 DB의 정보 부족 한계를 **LLM Tool**을 통한 실시간 외부 정보 탐색으로 확장함,
	    - **FastAPI**와 **SQL Agent**로 구조화하여 유학원마다 파편화된 정보를 한눈에 조망할 수 있는 넓은 시야를 제공함
        
### **[2] Clear Vision: 명확한 전망**

> **목표:** STT/TTS와 RAG 기술로 실제 인터뷰 환경을 구현하고 합격 가능성을 데이터로 가시화함

-   **멀티모달 AI 비자 시뮬레이션**: **STT/TTS** 기반의 '실전/연습 모드'를 통해 35%의 비자 거절 불확실성을 정면 돌파함
  
    -   **[한계 극복]** 
	    - 주관적 판단에 의존하던 기존 방식을 RAG 기반 정보 일치성 검토, 언어 문법 및 음성 분석(속도·유창성 등)의 다각도 평가를 수행함
	    - 단순 조언을 넘어 합격/불합격 여부, 개선점, 문항별 추천 답변이 포함된 최종 분석 리포트를 제공함으로써 준비 과정의 가시성을 확보하고 명확한 합격 결과를 설계함
        
        
### **[3] 통합 플랫폼 (Integrated Platform): 입시 챗봇과 비자 모의 인터뷰 서비스를 하나로 잇는 유학 솔루션**

>**목표**: Django와 AWS RDS 인프라를 활용하여, 입시 정보 챗봇과 비자 인터뷰 시뮬레이션을 한 플랫폼 내에 통합 구축함

-   **독립적 핵심 기능의 플랫폼화**:
	- 입시 정보 챗봇: 파편화된 전 세계 대학 데이터를 체계적으로 구조화하여, 방대한 모집요강을 즉각적으로 탐색할 수 있는 전문 챗봇 환경 구축
	- 비자 인터뷰 시뮬레이션: 실제 영사와의 인터뷰 환경을 재현하여 실전 대응력을 높이는 독립적인 AI 트레이닝 모듈 구현
    
    -   **[한계 극복]** 
		- 서비스 간 경계 제거: 입시와 비자로 파편화된 유학 준비 과정을 단일 플랫폼에 집약하여, 정보 탐색의 비효율과 실전 대비의 막연함을 동시에 해결함
    	- 고비용 구조 개선 : 특정 유학원에 종속된 고비용·폐쇄적 정보 구조를 탈피하고, 누구나 고도화된 기술 서비스를 저비용으로 누릴 수 있는 유학 준비의 대중화를 실현함


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
