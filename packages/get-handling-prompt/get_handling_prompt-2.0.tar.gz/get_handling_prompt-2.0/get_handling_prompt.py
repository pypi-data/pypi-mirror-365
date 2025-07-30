import pandas as pd
import ast

df = pd.read_excel('handing_measures_test_data.xlsx').fillna('')
context = ""

def get_handle_content(index, row):
    title_1 = f"{index+1}.完整链涉3类设备日志ID号：{row['mail_id']}-{row['edr_id']}-{row['dns_ids']}"
    title_2 = f"攻击链阶段\t\t\t智能体处置措施"
    handle = ""
    for k,v in ast.literal_eval(row['yll']).items():
        handle += f"{k}\t\t\t{v}\n"
        # if k == 'DNS隧道通信建立':
        #     handle += f"{k}\t\t{v}\n"
        # else:
        #     handle += f"{k}\t\t\t{v}\n"
    return f"{title_1}\n{title_2}\n{handle}"

for index, row in df.iterrows():
    context += get_handle_content(index, row)

with open('test.txt','w',encoding='utf-8') as f:
    f.write(context)