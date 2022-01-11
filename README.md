# 몰입캠프 2주차 여행 계획 앱 Traveler
## 팀원
김민결, 차다윤
## ABSTRACT
> 여러 친구들과 함께 여행을 갈 때, 모든 사람의 의견이 반영될 수 있는 계획을 짜는 것은 힘든 일이다.  
Traveler는 여러 사람이 함께 여행 계획을 편리하게 짤 수 있도록 도와주는 앱이다.

## Backend
> Link: https://github.com/MadCamp-Week2/Project02_backend
> #### Server framework : Django
> #### Database : Sqlite (Django에서 기본 제공)
>> 어플리케이션에서 사용하는 다음 항목에 대하여 모델을 구축함
- User: 이메일, 패스워드를 포함한 각 유저의 정보
- Place: 여행지
- Travel: 여행 정보
- Schedule: 각 여행에 포함되는 세부 스케줄들의 정보
- Profile: 앱 내 유저의 프로필 정보
> 안드로이드 클라이언트 측에서 retrofit을 통해 request를 보내면, 백엔드는 해당 request에 알맞게 데이터베이스를 수정하고, 필요 정보를 제공함.

##Frontend
> Link: https://github.com/MadCamp-Week2/Project02
