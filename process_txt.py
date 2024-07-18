import pandas as pd
import datetime
import regex as re
from tqdm import tqdm
import time 
import pathlib
import time
import explore
import typing

def load_save_state(csv_name):
    df = pd.read_excel(pathlib.Path("chats_processed",csv_name))
    arr_datetime = df['datetimes'].dt.to_pydatetime()
    df['datetimes']= pd.Series(arr_datetime, dtype=object)
    return df

def preprocess_lines(all_lines:typing.List[str]):
    all_lines = all_lines.split("\n")
    # some messages contain "\n", so we have to append those messages to the last message,
    # they belong to that one
    regex_separators = re.compile(r'\[[0-9]{1,2}\.[0-9]{1,2}\.[0-9][0-9], [0-9]{1,2}\:[0-9][0-9]\:[0-9][0-9]\]')
    split_on = "."
    if len(regex_separators.findall(all_lines[0])) == 0:
        regex_separators = re.compile(r'\[[0-9]{1,2}\/[0-9]{1,2}\/[0-9][0-9], [0-9]{1,2}\:[0-9][0-9]\:[0-9][0-9]\]')
        split_on = "/"
    all_lines_clean = []
    for line in tqdm(all_lines,desc="Processing text"):
        if len(regex_separators.findall(line)) == 1:
            all_lines_clean.append(line)
        elif len(regex_separators.findall(line)) == 0:
            all_lines_clean[-1] = " ".join([all_lines_clean[-1],line])
        else:
            print(regex_separators.findall(line))
    return all_lines_clean,split_on

def convert_to_pandas(all_lines_clean,split_on):
    times = []
    dates = []
    datetimes = []
    authors = []
    texts = []
    for i in tqdm(range(len(all_lines_clean)),desc="Parsing"):
        try:
            int(all_lines_clean[i].split(",")[0][1:].split(split_on)[0])
        except:
            all_lines_clean[i] = all_lines_clean[i][1:]
        dates.append(all_lines_clean[i].split(",")[0][1:])
        day=int(dates[-1].split(split_on)[0])
        all_lines_clean[i] = all_lines_clean[i].replace("["+dates[-1]+", ","")
        times.append(all_lines_clean[i].split("]")[0])
        all_lines_clean[i] = all_lines_clean[i].replace(times[-1]+"] ","")
        author = all_lines_clean[i].split(":")[0]
        authors.append(author)
        all_lines_clean[i] = all_lines_clean[i].replace(authors[-1]+": " ,"")
        texts.append(all_lines_clean[i])
        datetimes.append(datetime.datetime(year=2000+int(dates[-1].split(split_on)[-1]),
                                        month=int(dates[-1].split(split_on)[1]),
                                        day=day,
                                        hour=int(times[-1].split(":")[0]),
                                        minute=int(times[-1].split(":")[1]),
                                        second=int(times[-1].split(":")[2])
                                        ))
    print("Creating pandas dataframe...")
    df = pd.DataFrame(
        {
            'Date':dates,
            'Time':times,
            'Author':authors,
            'Message':texts,
            'datetimes':datetimes
        }
    )
    df['Number_words'] = df['Message'].apply(lambda x: len(x.split(" ")))
    df['Message_len'] = df['Message'].apply(lambda x: len(x))
    return df

def write_excel(df,excel_name) -> None:
    try:
        df.to_excel(pathlib.Path("chats_processed",excel_name),index=False, engine="openpyxl")
    except:
        df.to_excel(pathlib.Path("chats_processed",excel_name),index=False,engine='xlsxwriter')

def to_pandas_save(filename:str,owner:str) -> pd.DataFrame:
    with open(pathlib.Path("chats",filename)) as f:
        all_lines = f.read()
    all_lines_clean,split_on = preprocess_lines(all_lines)
    df = convert_to_pandas(all_lines_clean,split_on)

    print("Filter messages")
    # filter control messages
    faulty_authors = ['\u200eDu','Du']
    df_control_messages = pd.DataFrame()
    for author in faulty_authors:
        df_control_messages = pd.concat([df_control_messages,df[df['Author'] == author].copy()])
        df = df.drop(df[df['Author'] == author].index)
    df = df.drop(df[df['Message'] == "\u200eNachrichten und Anrufe sind Ende-zu-Ende-verschlüsselt. Niemand außerhalb dieses Chats kann sie lesen oder anhören, nicht einmal WhatsApp."].index)

    # delete control messages like "Du hast das Gruppenprofilbild geändert"
    df_control_messages = pd.concat([df_control_messages,df[df['Author'] == df['Message']].copy()])
    df = df.drop(df[df['Author'] == df['Message']].index)

    # filter stuff like video calls
    videocall_indices = []
    for i,r in df.iterrows():
        if r['Message'] == r['Author']+" hat einen Videoanruf gestartet" or \
            " ".join(r['Message'].split(" ")[0:3]) == '\u200e\u200eDeine Sicherheitsnummer für' or \
            " ".join(r['Message'].split(" ")[0:3]) == '\u200eDeine Sicherheitsnummer für':
            videocall_indices.append(i)
    df_control_messages = pd.concat([df_control_messages,df.loc[videocall_indices].copy()])
    df = df.drop(videocall_indices)

    df_control_messages['Message'] = df_control_messages['Message'].apply(lambda x: x.replace("Du hast",owner+" hat"))
    df_control_messages['Message'] = df_control_messages['Message'].apply(lambda x: x.replace("Du wurdest",owner+" wurde"))
    df_control_messages['Message'] = df_control_messages['Message'].apply(lambda x: x.replace("Du bist",owner+" ist"))
    df_control_messages['Message'] = df_control_messages['Message'].apply(lambda x: x.replace("\u200e",""))
    df_control_messages['Author'] = df_control_messages['Author'].apply(lambda x: x.replace("Du hast", owner+" hat"))
    df_control_messages['Author'] = df_control_messages['Author'].apply(lambda x: x.replace("Du wurdest", owner+" wurde"))
    df_control_messages['Author'] = df_control_messages['Author'].apply(lambda x: x.replace("Du bist", owner+" ist"))
    df_control_messages['Author'] = df_control_messages['Author'].apply(lambda x: x.replace("\u200e",""))
    df_control_messages['Author'] = df_control_messages['Author'].apply(lambda x: x.replace("Du",owner))

    for i,r in df_control_messages.iterrows():
        # print(r['Author'].split(" "))
        # print(r['Author'].split("hat"))
        # print(r['Author'].split("wurde"))
        # print(r['Author'].split("ist"))

        if len(r['Author'].split("hat")) == 2:
            split_on = "hat"
        elif len(r['Author'].split("wurde")) == 2:
            split_on = "wurde"
        elif len(r['Author'].split("ist")) == 2:
            split_on = "ist"
        df_control_messages.at[i,"Author"] = r['Author'].split(split_on)[0]
    df_control_messages['Author'] = df_control_messages['Author'].apply(lambda x: x.strip())
    print(df['Author'].unique())

    print("Writing excel...")
    write_excel(df,filename.split(".")[0]+".xlsx")
    # write_excel(df_control_messages,filename.split(".")[0]+"_control_messages.xlsx")
    print("Finished writing excel")
    return df,df_control_messages