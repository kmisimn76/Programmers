# 동적K 실험

### 동적 K 의미성 실험

동적 K는 시시때때 변하는 CPU 환경에 적응적으로 최적화 하기 위한 방법이다.

개인적으로 가장 좋을 거 같은 시나리오는, 큰 부하 프로세스가 들어오는 상황임.

APK는? 미리 프로파일할 수 있으니까 시나리오가 제한적일 것. 더 현실적인걸 해봐야지.

또 gpu freq도 조절할 수 있다면 좋을 거 같은데...

- 1.  부하프로세스 생성
    - 프로세스 명세
        - CPU 사용률 차지하도록, 다른 프로세스가 느려지도록 하는 부하로. 10초 이상 유지
        - 각 보드에서 수행. 크로스컴파일 필요
        - /home/abab2365/workspace/KLO/Qualcomm_exp/cpu_overhead/
        - overhead.cpp : 본체
            - sleep을 통해 부하 조절, 반복횟수 설정 가능하도록. 추가로 cpu 사용률 높이기 위해 inner loop도 필요

            ```python
            for i in range(2^(log_outer_iter)):
            	for j in range(inner_iter):
            		sum += rand()
            	sleep(Tsleep)
            print(sum)
            ```

            - 사용법: ./overhaed [T_sleep(us)] [inner_iter] [log_iter]
            - 실행 결과
                - ./overhead 10 1000 20 : qualcomm CPU **45%** utilization, Note10 **65%** util
                - ./overhead 1000 100000 20 : qualcomm CPU **71%** utilization, Note10 **78%** util
                - ./overhead 1000 5000 20 : qualcomm CPU **23%** utilization, Note10 CPU **43%** util
    - [x]  CPU를 적당히 쓰는 부하 프로세스, 10초 이상 유지하도록
    - [x]  CPU 사용률 체크
    - 여기서 git submit
- 2.  부하프로세스와 KLO측정 프로세스 동시에 수행하여 최적 K 실험
    - [x]  동시에 수행하도록 환경조성(script?)
        - adb로 overhead 실행시킨 뒤,
        - adb에 killall -9 overhead 로 마지막에 overhead 부하 끄기
    - [ ]  동시에 수행하여, ACL예제의 T_prod, T_ker 측정
    - [ ]  상수, 정적, 동적K 계산
        - 단순동시수행 결과
            - 상수 최적K 차이가 아예 안나네???
            - 이거 랜덤 LUT로 한거였네;;; 실험 다시.
            - 다시해도 변화 없음
            - tidle 측정이 안됐길래 식겁했는데, 그냥 마지막 출력이 안된거였음. 그냥 돌리는거만으로 tidle 변화를 유도할수는 없는 듯.
            - Taskset 문제는 아닐지, T_prod는 차이가 발생한건지...
            - tidle 조절할 수 없는 요인
                - CPU clock
                    - tidle은 실질적으로 ???? 아니 설명은안되는데, clock은 tidle 시간에 별로 영향주지 못함. 편차때매 big core 할당하긴함..
                - without taskset Overhead
                    - 아마 taskset을 안했으니 원래 수행하던 추론 프로세스에는 영향주지 못했을 것. 아예 프로세스가 많다면?? 모를까.. 여러개실행해볼까?
            - Taskset 조절
                - 단순히 하나의 big core만 사용하기 위해 taskset 10과 같이 하면, 금방 비활성화되어 invalid cpu 에러 발생
                - 따라서, 최소한 매우 작은 부하를 가지고 오래가는 임의부하를 해당 코어에만 실행시켜서 비활성화 되지 않도록 함 →언젠간 invalid taskset.. 못해먹겠다
                - 그냥 부하프로세스를 모든 코어에 할당하기.@@
        - 4개프로세서 동시수행
            - 음.. 평균 T_prod는비슷한데, 그 이유가 다른게 아니라 첫번째 T_prod가 너무 커서 다른 T_prod 평균이 비슷해져버린 것..
            - 따라서 첫번째 T_prod가 뭔지, 그거를 mean에 포함시키면 안됨
            - → mean 출력하는 부분은?
            - 첫번째 t_idle은 잘못 측정된 값일 것(기준이 되는 시작클럭이 없는 상태). 설정이 중요한데.. 일단은 tests/framework/Framework.cpp에 첫번째 mean_t_idel은 0으로 설정..
            - 처음 잘못 K 설정하지 않기위해, 처음 t_prod는 mean t_prod로 사용? → run_example.cpp에 적용

        실험을 이렇게 복잡하게 해야하는 이유

        - 수행시간 측정 편차를 줄이기 위해 big core에만 할당해 자연스러운 예제를 만들기가 어려워 이렇게 했으나, 실제 수행환경은 APK일 것이므로 이는 little core에 할당될 확률이 높고(android 스케줄러), little core는 background task가 많을 것이므로 유동적인 환경이 조성될 것으로 생각함.
        - Android(APK) 태스크로 미리 줘버리면, 임의의 일정한 부하 환경 조성이 어려워 실험 결과 해석이 더 어려울 것이란 생각. 아닐수도있고. 근데 애초에 ACL은 APK로 못만들겠고, TFLite도 쉽지 않음.
        - 12/02 진행상황
            - 코드 클리닝하면서 약간의 문제 → 원래 논문쓸때에는 producing time 숫자 출력이 제대로 됐었는데(그거 바탕으로 결과 얻음) 안되네
            - → producing time 코드 수정
                - 사소한 디버깅 → 첫커널 t_prod=0인데 평균 나눗셈을 바로 length로 해버려서, length-1로 바꿈
                - 하 producing time 안변하네? 대체 뭘 해야 변하는거지?
                - 화나.. 그냥 모든 코어에 다 돌려버려. 이거 해서 되면 opencl 런타임이 little core에서 안느리게 잘 동작했던거다 그런거겠지?
                    - !!!! t idle 변화 유의미!@!!
                    - 재확인실험 진행
            - 1차 실험결과: 부하 프로세스에 따라 T_prod 변화 관찰

                [부하프로세스에 따른 T_prod(us)](https://www.notion.so/8479e7097cae450b8a91c29b33a2448e)

                ![%E1%84%83%E1%85%A9%E1%86%BC%E1%84%8C%E1%85%A5%E1%86%A8K%20%E1%84%89%E1%85%B5%E1%86%AF%E1%84%92%E1%85%A5%E1%86%B7%20b963f2f730454e29ab2daf9743f022c4/Untitled.png](%E1%84%83%E1%85%A9%E1%86%BC%E1%84%8C%E1%85%A5%E1%86%A8K%20%E1%84%89%E1%85%B5%E1%86%AF%E1%84%92%E1%85%A5%E1%86%B7%20b963f2f730454e29ab2daf9743f022c4/Untitled.png)

            - 2차실험→12/3 이어서.: 각 코어에 1개 프로세스만 실행했는데, 더 많이 실행하면 오버헤드가 더 늘어나지 않을까? 실험.

                [부하프로세스에 따른 T_prod(us) - 각 코어 별 2개 부하](https://www.notion.so/fd8b82674b4e499b8c4688368bd739e8)

                → 음.... 이런 ㅅㅂ 왜안돼

                → CPU Utilization은 T_prod에 제한적인 영향을 미침.

                T_prod는 어떤걸로 이루어져있나?

                → 커널 런치 사이의 시간이므로 커널 인큐에 필요한 인자들, 딥러닝 레이어 파라미터를 계산하고, 여러 함수 call이 대부분을 차지할 것

                →T_idle은 매우 짧을 것이기 때문에 CPU Utilization이 높더라도 그 사이 계산하는데 context switching 거의 없어서 T_idle에 영향 없다고 보는게 합리적일 듯

                →그냥 freq 줄이는게 답인데, 이게 영향이 없다는 거지.. freq 변화해서 한번만 더 검증

            - 2.5차실험 → CPU Freq 바꾸어서 T_idle 변화 측정하는 재실험
                - 예상결과; CPU freq가 바뀌었으니, T_idle 연산인 파라미터연산 등이 당연히 시간 영향 받을거니까 T_idle이 clock rate에 비례해 줄어야 함.
                    - 가정: T_idle은 여러 인자, 레이어 파라미터 계산하는 시간이다.
                - 지난번에 bigcore만 freq 낮췄구나..
                - bigcore에서 도는게 맞다면 상관없지 않나..?
                - **실험결과**, F_min에서 일부 네트워크는 Kopt,minfreq보다 Kopt,maxfreq가 오히려 성능 좋은 문제.
                    - 당연히 동적K도 성능 좋지 않고..
                    - LUT가 F의 함수로 이루어져있다던가.. → 이러면 좀 곤란한데..
                        - → **1.** 이걸 먼저 확인할까?
                        - **→** LUT가 바뀌어서 freq 바꾼 이후로도 opt는 아닐 수 있음.. 그런데 LUT **막 그렇게 바뀐거 같지는 않음..**

                            ![%E1%84%83%E1%85%A9%E1%86%BC%E1%84%8C%E1%85%A5%E1%86%A8K%20%E1%84%89%E1%85%B5%E1%86%AF%E1%84%92%E1%85%A5%E1%86%B7%20b963f2f730454e29ab2daf9743f022c4/Untitled%201.png](%E1%84%83%E1%85%A9%E1%86%BC%E1%84%8C%E1%85%A5%E1%86%A8K%20%E1%84%89%E1%85%B5%E1%86%AF%E1%84%92%E1%85%A5%E1%86%B7%20b963f2f730454e29ab2daf9743f022c4/Untitled%201.png)

                    - → 낮은 freq는 LUT 정확도 문제로 인해 잘 측정이 안된 거라던가?
                    - → F_max에서 Kopt,minfreq가 Kopt,maxfreq보다 모두 성능이 안좋다면?
                        - → 좋다면? Kopt,max가 실제 Kanswer,maxfreq와 같은지 확인
                        - → Kopt,minfreq가 실제 Kanswer,maxfreq인 경우가 있는지도 확인
                    - → **2.** 아니, 애초에 Kanswer,minfreq를 구해서 비교해보고 Kopt,minfreq가 너무 동떨어져있다면? Kopt,maxfreq가 오히려 더 가깝다면? 그냥 Kopt 구할 때 문제.. → 이러면 LUT 구하는 방법에서 문제를 찾아야, 아니면 생각하기 싫지만 상수Kopt 구하는 방법이 문제.
                        - *참고 → ACL_manual_K에 직접 수동 K 구하는 매크로 프로그램 작성
                    - → 2.번 실험 결과 Kanswer,minfreq가, Kopt,minfreq보다 Kopt,maxfreq에 유사하다면
                        - K_opt,minfreq 구하는 방법이 문제?
                    - 만약 Kanswer,minfreq가 maxfreq에서와 거의 변하지 않는다면
                        - freq(t_prod)는 K에 큰 영향이 없는 것? 일단 LUT 상에서는 그렇지 않으니 그럴 확률 희박. 예전에 증명하기도 했던거같고.
                        - **거의 변하지 않는데..?**
                        - 대응이 가능한가?
                    - 결론이 될 가능성이 가장 높은 것
                        - → ~~LUT가 freq에 따라 달라짐. Freq가 달라지면 KLO 요인이 달라지니 LUT도  달라질 것.~~. 1.에서 처럼 그렇게 바뀐건 없어서 틀림.. 어렵다 그냥 ACL 코드를 바꿔버릴까?
                    - ..다만 현재 상수 Kopt 구하는 방법이 굉장히 간단하고, 이게 장점이 될 것이기 때문에(아니라면 그냥 직접 k 구하는게 더 낫겠지..) 이 방법을 그냥 버리긴 아까움
                    - 결론 → 상수K 성능이 freq 변화에도 그렇게 낮아지지  않는 문제
                    - →LUT가 Freq에 영향 받는건 아닌지→ 확인 결과 ..
                    - → manual_K_minfreq가 manual_K_maxfreq와 거의 비슷함 → LUT가 별로 변하지 않고 T_prod는 크게 변했는데, manual_K는 거의 비슷?  → LUT 봐도 그렇게 변하지 않는 구간이 있네..? 애초에 constant K 가 바뀌었으니 그 부분에 해당하는 것은 아님.
            - 3차실험→그 후: GPU execution time을 늘려보는 실험. GPU의 clock을 낮췄으면 좋겠고, profile overhead는 추가될 것

    - 실험리스트
        - [ ]  기존 상수K, 부하상수K값 확인
        - [ ]  기존 상수 K, 부하 상수 K speedup 측정
        - [ ]  동적K 기존, 부하 speedup 측정
    - 실험결과체크리스트
        - [ ]  기존 상수K와 부하 상수K가 달라지는지 확인
        - [ ]  기존 상수K로 하면 speedup이 낮아지는지 확인
        - [ ]  부하 상수K로 하면 speedup이 유지되는지 확인
        - [ ]  동적K는 기존과 부하 모두 비슷한 speedup 갖는지 확인

    - [ ]  결과 정리
- 3. GPU Freq 조절
- 4. GPU Freq 조절해서 최적 K 실험
    - [ ]  그냥 T_prod, T_ker가 얼마나 달라지는지 측정
    - [ ]  최적K 계산