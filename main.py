import pandas as pd
import time
import explore
import process_txt


def explore_df(df,df_control_messages):
    authors = list(df['Author'].unique())
    # start = time.time()
    explore.explore_number_messages(df,authors)
    # print("explore_number_messages took {}".format(time.time() - start))
    # start = time.time()
    explore.extract_longest_messages(df,authors)
    # print("extract_longest_messages took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_time_to_answer(df,authors)
    # print("explore_time_to_answer took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_times(df,authors)
    # print("explore_times took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_specific_words(df,authors)
    # print("explore_specific_words took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_word_count(df,authors)
    # print("explore_word_count took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_emoji_usage(df,authors)
    # print("explore_emoji_usage took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_longest_no_contact(df,authors)
    # print("explore_longest_no_contact took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_daily_number_messages(df,authors)
    # print("explore_daily_number_messages took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_daily_number_messages_graphically(df,authors)
    # print("explore_daily_number_messages_graphically took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_number_of_shared_links(df,authors)
    # print("explore_number_of_shared_links took {}".format(time.time() - start))
    # start = time.time()
    explore.explore_double_texting(df,authors)
    # print("explore_double_texting took {}".format(time.time() - start))


    # authors_control_messages = df_control_messages['Author'].unique()
    # authors_control_messages_dict = [{
    #         'Videocalls' : 0,
    #         'Phone_change' : 0,
    #         'Group_left':0,
    #         'Group_joined':0,
    #         'Group_kicked':0,
    #         'Admin_promotion':0,
    #         'Admin_demotion':0,
    #         'Group_pic_changed':0,
    #         'Group_desc_changed':0,
    #         'Numb_people_added':0
    #     }] * len(authors)
    

# clustering mit k-means und transformers zum topic extraction keyword über was so geschrieben wurde?
# -> todo, das datum hinzufügen, wann man am längsten mal nicht geschrieben hat

if __name__ == "__main__":
    df,df_control_messages = process_txt.to_pandas_save("example.txt",'Jane')    
    explore_df(df,df_control_messages)
