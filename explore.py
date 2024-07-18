import pandas as pd
import datetime
import regex as re
import matplotlib.pylab as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
import emoji_regex
from stopwords import stopwords

WORDLIST = ['Football','Love','Friends','miss']

def explore_number_messages(df,authors):
    print("total number of messages: {}".format(len(df)))
    print(authors)
    for a in authors:
        num_messages = len(df[df['Author']==a])
        print("{} wrote {}".format(a, num_messages))
        total_length = df[df['Author'] == a]['Message_len'].sum()
        print("Average length of messages written by {} was {} ".format(a,round(total_length/num_messages,2)))
    
def extract_longest_messages(df,authors):
    print("Overview of longest messages")
    authors_longest_message = {}
    for a in authors:
        authors_longest_message[a] = df[df['Author'] == a].sort_values(by = 'Message_len',ascending = False).iloc[0]['Message']
    print(dict(sorted(authors_longest_message.items(), key=lambda item: len(item[1]))))
    for a in list(authors_longest_message.keys()):
        print("The longest message sent by {} with length {} was :\n {} \n".format(a,len(authors_longest_message[a]),authors_longest_message[a]))


def explore_time_to_answer(df,authors):
    # antwortzeit
    number_of_answers = [0] * len(authors)
    wait_time_minutes = [0] * len(authors)
    last = None
    for i,row in df.iterrows():
        try:
            if last == None:
                last = row
                continue
        except:
            pass
        if last['Author'] != row['Author']:
            author = row['Author']
            index_author = authors.index(author)
            number_of_answers[index_author] += 1
            diff = row['datetimes'] - last['datetimes']
            diff_minutes = (diff.days * 24 * 60)
            wait_time_minutes[index_author] += diff_minutes
        last = row
    try:
        [print("{} waited on average {} minutes to respond".format(authors[a],round(wait_time_minutes[a]/number_of_answers[a],2))) for a,_ in enumerate(authors)]
    except:
        pass
    
def explore_times(df,authors):
    # Uhrzeiten an denen geschrieben wurde
    message_times =  [[] for _ in range(len(authors))]
    for i,r in df.iterrows():
        hour = r['Time'].split(":")[0]
        author_index = authors.index(r['Author'])
        message_times[author_index].append(int(hour))
    # print(message_times)
    for i in range(len(authors)):
        plt.hist(message_times[i],bins = 24)
        plt.title("Times when {} wrote messages".format(authors[i]))
        plt.xlabel("Time of day (h)")
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.show()

def explore_specific_words(df,authors):
    # number of times people said unsavory words
    # convert all messages to type string
    df['Message'] = df['Message'].apply(lambda x: str(x))
    for w in WORDLIST:
        for a in authors:
            print('{} said {} {} many times'.format(a,w," ".join((df[df['Author'] == a].Message)).lower().count(w)))
        print(" ")

def explore_emoji_usage(df,authors):
    print("Whats the emoji usage like?")
    EMOJI_RAW = emoji_regex.EMOJI_RAW
    EMOJI_REGEX = re.compile(EMOJI_RAW)
    for a in authors:
        print("{} used {} emojis in total".format(a,len(EMOJI_REGEX.findall(" ".join(df[df['Author'] == a].Message)))))

def word_counts_dict(word_dict,word):
    word = word.lower()
    if word_dict.get(word) == None:
        word_dict[word] = 1
    else:
        word_dict[word] += 1

def explore_word_count(df,authors):
    # todo ignore stopwords
    print("What are the most frequently used words?")
    for a in authors:
        # count words
        word_dict = {}
        [word_counts_dict(word_dict,word) for sentence in df[df['Author'] == a].Message for word in sentence.split(" ")]
        # sort dict
        word_dict = dict(reversed(sorted(word_dict.items(), key=lambda item: item[1])))
        for s in stopwords:
            try:
                del word_dict[s]
            except:
                pass
        print("Word frequency for {} : {}".format(a,[(word,word_dict[word]) for word in list(word_dict.keys())[0:15]]))

def explore_longest_no_contact(df,authors):
    time_without_responding_author = {}
    for a in authors:
        time_without_responding_author[a] = [0,None]
    last = None
    for i,row in df.iterrows():
        try:
            if last == None:
                last = row
                continue
        except:
            pass
        if row['Author'] != last['Author']:
            time_without_responding = (row['datetimes'] - last['datetimes']).total_seconds()
            if time_without_responding > time_without_responding_author[row['Author']][0]:
                time_without_responding_author[row['Author']][0] = time_without_responding
                time_without_responding_author[row['Author']][1] = row['datetimes']
        last = row.copy()
    for a in authors:
        try:
            print("Longest time {} hasnt texted, was {}h on {}".format(a,round(time_without_responding_author[a][0]/3600,1),time_without_responding_author[a][1].strftime("%y-%m-%d")))
        except:
            pass


def explore_daily_number_messages(df,authors):
    df_daily_messages = df.copy()
    df_daily_messages['mdy'] = df['datetimes'].apply(lambda x: x.strftime('%m-%d-%y'))
    for a in authors:
        df_author = df_daily_messages[df_daily_messages['Author'] == a]
        first_day = df_author['datetimes'].iloc[0]
        last_day = df_author['datetimes'].iloc[len(df_author)-1]
        total_days = (last_day - first_day).days
        df_author_grouped = df_author.groupby(['mdy'])['Message'].count().sort_values(ascending=False)
        print("As a maximum, {} has texted {} many times on {}".format(a,
                                                                                                     df_author_grouped.max(),
                                                                                                     df_author_grouped.idxmax(),
                                                                                                     df_author_grouped.min()))
        print("On days messages were exchanged, the average number of messages was {} and on all days the average was {}".format(round(df_author_grouped.mean(),1),
                                                                                         round(df_author_grouped.sum()/total_days,1)))

def explore_daily_number_messages_graphically(df,authors):
    df_daily_messages = df.copy()
    df_daily_messages['mdy'] = df['datetimes'].apply(lambda x: x.strftime('%m-%d-%y'))
    first_day = df_daily_messages['datetimes'].iloc[0]
    last_day = df_daily_messages['datetimes'].iloc[len(df_daily_messages) - 1]
    days = [first_day.strftime('%m-%d-%y')]
    while first_day.strftime('%m-%d-%y') != last_day.strftime('%m-%d-%y'):
        first_day = first_day + datetime.timedelta(days = 1)    
        days.append(first_day.strftime('%m-%d-%y'))
    author_dict_messages = {}
    for a in authors:
        y_number_of_messages_list = []
        df_author = df_daily_messages[df_daily_messages['Author'] == a]
        for day in days:
            y_number_of_messages_list.append(len(df_author[df_author['mdy'] == day]))
        author_dict_messages[a] = y_number_of_messages_list
    fig, ax = plt.subplots()
    ax.plot(days,np.reshape([np.array(messages,dtype=np.int64) for messages in author_dict_messages.values()],(len(days),len(authors))),label=authors,alpha = 0.5)
    first_day = df_daily_messages['datetimes'].iloc[0]
    # ax.set_xticks(np.arange(0,len(days),(last_day-first_day).days/14))

    ax.xaxis.set_major_locator(MaxNLocator(5))
    plt.title("Number of messages per day")
    ax.legend()
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.show()

def create_or_add_to_dict_links(mydict,ele,pattern_http_beginning,known_hosts):
    findings = pattern_http_beginning.findall(ele)
    for f in findings:
        ele = ele.replace(f,"")
    if known_hosts.get(ele) != None:
        ele = known_hosts[ele]
    if mydict.get(ele) == None:
        mydict[ele] = 1
    else:
        mydict[ele] += 1

def explore_number_of_shared_links(df,authors):
    known_hosts = {
        'youtu.be': "www.youtube.com",
        'maps.app.goo.gl' : 'maps.google.com'
    }
    link_prefix = ['http:','https:']
    for a in authors:
        df_author = df[df['Author'] == a]
        dict_links = {}
        for l in link_prefix:
            my_link_pattern = re.compile(r'\b'+re.escape(l)+'\/\/[^\/ | \s]*')
            pattern_http_beginning = re.compile(r'https:\/\/|http:\/\/')
            [create_or_add_to_dict_links(dict_links,ele,pattern_http_beginning,known_hosts) for x in df_author['Message'] for ele in my_link_pattern.findall(x)]
        # print(dict_links)
        dict_links = sort_dict_by_value(dict_links)
        try:
            print("{} shared {} links from the following sources: \n {}: {} \n {}: {} \n {}: {} ".format(a,
                                                                                                                      sum(list(dict_links.values())),
                                                                                                                      list(dict_links.keys())[0],dict_links[list(dict_links.keys())[0]],
                                                                                                                      list(dict_links.keys())[1],dict_links[list(dict_links.keys())[1]],
                                                                                                                      list(dict_links.keys())[2],dict_links[list(dict_links.keys())[2]],))
        except:
            pass


def count_emojis(text,regex_pattern):
    count = len(regex_pattern.findall(text))
    return count


def sort_dict_by_value(mydict):
    return dict(reversed(sorted(mydict.items(), key=lambda item: item[1])))

def explore_double_texting(df,authors):
    doubling_texting_time = 240 # double texting starting at 4 minutes (240 seconds)
    number_of_double_textings = [0] * len(authors)
    average_double_texting_time = [0] * len(authors)
    last = None
    for i,row in df.iterrows():
        try:
            if last == None:
                last = row
                continue
        except:
            pass
        if last['Author'] == row['Author']:
            diff = row['datetimes'] - last['datetimes']
            diff_seconds = diff.seconds
            if diff_seconds > doubling_texting_time:
                # double texting detected
                author = row['Author']
                index_author = authors.index(author)
                number_of_double_textings[index_author] += 1
                average_double_texting_time[index_author] += diff_seconds
        last = row
    for a,_ in enumerate(authors):
        try:
            print("{} double texted {} times where on average {} minutes passed between two double texts".format(authors[a],number_of_double_textings[a],round(average_double_texting_time[a]/number_of_double_textings[a]/60,1)))
        except:
            pass
    