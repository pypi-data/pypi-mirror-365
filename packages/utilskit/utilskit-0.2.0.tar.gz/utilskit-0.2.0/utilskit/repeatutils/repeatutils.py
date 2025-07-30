import sys
import os
import numpy as np


__all__ = ['get_repeat_section', 'get_stan_repeat_section']


def issame(value1, value2):
    # 서로 같은 경우
    if value1 == value2:
        return True
    # 서로 다른 경우
    else:
        # 어느 한 쪽 이라도 str type 인 경우
        if isinstance(value1, str) or isinstance(value2, str):
            if str(value1) == str(value2):
                return True # ex) value1 = 1, value2 = '1'
            else:
                return False # ex) value1 = 1, value2 = 'nan'
        # 어느 한 쪽이라도 str type 이 아닌 경우
        else:
            # value1 이 NaN 일때
            if np.isnan(value1):
                # value2 도 NaN 이면
                if np.isnan(value2):
                    return True
                # value2 가 NaN 이 아니면
                else:
                    return False
            else:
                return False


# def get_repeat_section2(data, repeat_num, refer_value=None, except_nan=True):
#     '''
#     '''
#     raw_ary = np.array(data)
#     ary = raw_ary.copy()
#     same_tf = (ary[:-1] == ary[1:])
#     is_nan = np.isnan(ary)

#     for i, j, k, l in zip(ary[:-1], ary[1:], same_tf, is_nan):
#         print(i, j, k, l)

#     a = np.where(same_tf==1)
#     print(a)

#     sys.exit()

#     value_list = []
#     start_idx_list = []
#     end_idx_list = []
#     start_idx = 0
#     # pre_value = 'nan'
#     repeat_num = 1    
#     for idx, value in enumerate(ary):
        
#         # 가장 처음인 경우
#         if idx == 0:
#             pre_value = value
#             continue
        
#         # 현재 값이 이전 값과 동일할때
#         if issame(value, pre_value):
#             repeat_num += 1

#         # 현재 값이 이전 값과 다를때
#         else:
#             if repeat_num >= stan_repeat:
#                 value_list.append(pre_value)
#                 start_idx_list.append(start_idx)
#                 end_idx_list.append(idx-1)
#             # 시작 지점 갱신 & 반복횟수 초기화
#             start_idx = idx
#             repeat_num = 1
#         pre_value = value

#     # 마지막 값이 이전 값과 같을때
#     if issame(value, pre_value):
#         if repeat_num >= stan_repeat:
#             value_list.append(value)
#             start_idx_list.append(start_idx)
#             end_idx_list.append(idx)
#     # --------------------------------------
#     # 함수 수정중
#     # 결과 정리
#     result = {'nan':None}
#     for v, si, ei in zip(value_list, start_idx_list, end_idx_list):
#         result[str(v)] = (si, ei)
#     if except_nan:
#         del result['nan']
#     return result



def get_repeat_section(data, repeat, except_nan=True):
    '''
    데이터 array 에서 정해놓은 반복 횟수 (stan_repeat) 만큼 반복되는 숫자구간이 있다면
    그 구간의 시작, 끝 위치 index 값을 추출한다.
    NaN 가 반복되는지 여부를 포함시킬 수 있다.
    '''
    ary = data.copy()

    value_list = []
    start_idx_list = []
    end_idx_list = []
    start_idx = 0
    # pre_value = 'nan'
    repeat_num = 1    
    for idx, value in enumerate(ary):
        
        # 가장 처음인 경우
        if idx == 0:
            pre_value = value
            continue
        
        # 현재 값이 이전 값과 동일할때
        if issame(value, pre_value):
            repeat_num += 1
            
        # 현재 값이 이전 값과 다를때
        else:
            if repeat_num >= repeat:
                value_list.append(pre_value)
                start_idx_list.append(start_idx)
                end_idx_list.append(idx-1)
            # 시작 지점 갱신 & 반복횟수 초기화
            start_idx = idx
            repeat_num = 1

        pre_value = value

    # 마지막 값이 이전 값과 같을때
    if issame(value, pre_value):
        if repeat_num >= repeat:
            value_list.append(value)
            start_idx_list.append(start_idx)
            end_idx_list.append(idx)
    # --------------------------------------
    # 함수 수정중
    # 결과 정리
    # print(value_list)
    # sys.exit()
    result = {}
    for v, si, ei in zip(value_list, start_idx_list, end_idx_list):
        try:
            result[str(v)].append((si, ei))
        except KeyError:
            result[str(v)] = [(si, ei)]
    if except_nan:
        del result['nan']
    return result


def get_stan_repeat_section(data, value, repeat, mode='a', reverse=False):
    '''
    ary 에서 기준값(stan_value)이 지정한 횟수(stan_repeat) 
    이상(above) 또는 이하(below) 만큼 반복되는 구간의 시작, 끝 위치 index 값을 추출하는 함수
    reverse 를 True 로 지정하면 해당 각 구간의 끝->시작, 시작->끝 으로 반전된다.
    mode 는 a (above) 와 b (below)만 존재
    '''
    ary = data.copy()

    start_idx = 0
    start_idx_list = []
    end_idx_list = []
    repeat_num = 1

    if len(ary) == 0:
        return [], []
            
    # stan_value = float(stan_value)
    for idx, val_ in enumerate(ary):

        # 가장 처음인 경우
        if idx == 0:
            pre_value = val_
            continue

        # 현재 값이 기준값(stan_value) 인 경우
        if issame(val_, value):
            # 이전값이 기준값과 동일하면
            if issame(pre_value, value):
                # 반복횟수 +1
                repeat_num += 1
            # 이전 값이 기준값과 다르면
            else:
                # 반복횟수 초기화
                repeat_num = 1
                # 현재 위치를 시작로 위치 지정
                start_idx = idx
        # 현재 값이 기준값과 다른 경우
        else:
            # 이전 값이 기준값과 동일하면
            if issame(pre_value, value):
                # idx 끝 위치 지정

                # 반복 횟수 기준 이상인 경우
                if mode == 'a':
                    # 기록된 반복 횟수가 기준 횟수 이상이면
                    if repeat_num >= repeat:
                        # 지정해둔 시작 위치 index 값을 구간시작 index 로 저장
                        start_idx_list.append(start_idx)
                        # 현재 위치 바로 이전 위치 index 값을 구간끝 index 로 저장
                        end_idx_list.append(idx-1)
                # 반복 횟수 기준 이하인 경우
                elif mode == 'b':
                    # 기록된 반복 횟수가 기준 횟수 이하면
                    if repeat_num <= repeat:
                        start_idx_list.append(start_idx)
                        end_idx_list.append(idx-1)
                elif mode == 'e':
                    # 기록된 반복 횟수가 기준 횟수와 동일하면
                    if repeat_num == repeat:
                        start_idx_list.append(start_idx)
                        end_idx_list.append(idx-1)
                else:
                    print('mode 를 a (above:이상), b (below:이하) 또는 e (equal:동일) 중 하나로 지정해주세요')
                    raise KeyError()
        # 현재 위치 값을 이전 위치로 저장
        pre_value = val_
    
    # 가장 마지막 데이터가 기준값과 동일한 경우
    if issame(val_, value):
        if mode == 'a':
            if repeat_num >= repeat:
                start_idx_list.append(start_idx)
                # 현재 위치 index 를 구간 끝 index 로 저장
                end_idx_list.append(idx)
        elif mode == 'b':
            if repeat_num <= repeat:
                start_idx_list.append(start_idx)
                end_idx_list.append(idx)
        elif mode == 'e':
            if repeat_num == repeat:
                start_idx_list.append(start_idx)
                end_idx_list.append(idx)
        else:
            raise KeyError('mode 를 a (above:이상), b (below:이하) 또는 e (equal:동일) 중 하나로 지정해주세요')
    # 가장 마지막 데이터가 기준값과 다르면 반복 계산할 필요 없음
    
    # 반전
    if reverse:
        rev_start_idx_list = [0]
        rev_end_idx_list = [len(ary)-1]
        for ns_idx, ne_idx in zip(start_idx_list, end_idx_list):
            if ns_idx == 0:
                rev_start_idx_list.pop(0)
                rev_start_idx_list.append(ne_idx+1)
                continue
            if ne_idx == len(ary)-1:
                rev_end_idx_list.pop(-1)
                rev_end_idx_list.append(ns_idx-1)
                continue
            rev_start_idx_list.append(ne_idx+1)
            rev_end_idx_list.insert(-1, ns_idx-1)
        
        start_idx_list = rev_start_idx_list.copy()
        end_idx_list = rev_end_idx_list.copy()
    
    # 결과 정리
    result = []
    for si, ei in zip(start_idx_list, end_idx_list):
        result.append((si, ei))

    return result