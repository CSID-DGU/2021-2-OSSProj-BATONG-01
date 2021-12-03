# 2021-2-OSSProj-BATONG-01
### Pygame을 이용한 Shooting Game
(original source: https://github.com/jpritcha3-14/shooting-game)
## Info
![badges](https://img.shields.io/badge/license-MIT-green.svg)
![badges](https://img.shields.io/badge/OS-ubuntu-red)
![badges](https://img.shields.io/badge/python-3.8.10-blue.svg)
![badges](https://img.shields.io/badge/vscode-1.59-yellow)

## 팀원 소개
* **팀장 : 동국대학교 바이오환경과학과** [**이희경**](https://github.com/HKLeeeee)
* **팀원 : 동국대학교 통계학과** [**노현영**](https://github.com/hyunyoung0724)
* **팀원 : 동국대학교 통계학과** [**안재혁**](https://github.com/wogur311)
* [BATONG's Notion Page](https://www.notion.so/2021-2-OSSP-BATONG-6c798b0fa0e74f52ab13c10d03274505)
## 게임 소개
#### 1. 시작화면
![images](https://github.com/wogur311/2021-2-OSSProj-BATONG-01/blob/main/data/%EB%B0%B0%EA%B2%BD%ED%99%94%EB%A9%B4.PNG?raw=true)
#### 2. 조작키
* **w a s d: 방향키**
* **space bar: 공격**
* **p: 일시정지**
* **b: 폭탄**
#### 3. 규칙
* **비행기로 미사일을 쏘아 적을 죽이면 점수를 얻을 수 있습니다. 적은 색깔별로 서로 다른 이동패턴을 가지고 있으며, 적을 죽였을때 얻는 점수는 아래와 같습니다.**

![image](https://user-images.githubusercontent.com/65498159/121726665-d43e1900-cb25-11eb-8862-d10e37284723.png)
* **비행기가 적과 충돌하면 우측 상단의 life가 줄어듭니다. life가 모두 사라지면 게임이 종료됩니다.**
* **폭탄, 쉴드, 적절반 아이템은 랜덤으로 드랍됩니다.** 
* **폭탄은 b키로 사용할 수 있고, 쉴드와 적절반 아이템은 획득시 자동 사용됩니다.**
* **쉴드 아이템은 적과 충돌을 1회 무효화시켜줍니다.**
* **적절반 아이템은 스테이지의 남은 적 수를 절반으로 줄여줍니다.**

## 실행방법
```shell
sudo apt-get update
```
   
```shell
pip install pygame
```
   
```shell
pip install pymysql
```

```shell
git clone https://www.github.com/CSID-DGU/2021-2-OSSProj-BATONG-01.git/
```
   
```shell
cd 
```
   
```shell
python3 shooting_game.py
```
