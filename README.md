# Manuscript
Predicting Counseling Behavioral Propensity Based on Temporal Return Visits Patterns and Current Perceived Intensity with Chronic Conditions Management

## Feature Dataframe
Index(['index', 'lastMod', 'askList', 'answerList', 'checkInList', 'complaint', 'record', 'advice', 'consultingType', 'patientVote', 'onlineCons', 'askLagTotal', 'answerLagTotal', 'checkInLag', 'checkInTitle', 'checkInType', 'withOffLine', 'timesCheckIn', 'askFreq', 'answerFreq', 'checkInFreq', 'satisficing', 'lookBackType1', 'lookBackLag1', 'lookBackType2', 'lookBackLag2', 'lookBackType3', 'lookBackLag3', 'lookAheadType', 'lookAheadLag', 'patientSex', 'patientAge'], dtype='object')  

## Criteria of Dataframe Inclusion and Exclusion
Totally, 383,278 pieces of return visits items were included after data preprocessing, including corpus about complaints, asking from patients, and answer from physicians.
### Access 
Original structured, semi-structured and unstructured chunks are crawled, and sentences in languages other than Chinese are replaced with null value and then jsonlized.
```python
def format(dataOri):
    idx = 0
    ask_list, answer_list, checkin_list, info_list = list(), list(), list(), list()
    #complaint_list, record_list, advice_list
    last_mod = ''
    dialogue = pd.DataFrame(columns=['num', 'lastMod', 'askList', 'answerList', 'checkInList', 'complaint', 'record', 'advice', 'patientInfo', 'consultingType', 'patientVote', 'onlineCons'])
    for i in range(len(dataOri)-1):
        if pd.isnull(dataOri.lastMod[i]) == False and dataOri.lastMod[i] != 'nan' and dataOri.lastMod[i] != '0':
            last_mod = dataOri.lastMod[i]
            if len(re.findall('\.', last_mod)) == 1:
                last_mod = '2022.' + last_mod
            info_list.append(dataOri.diseaseInfoList[i])
            info_list.append(dataOri.recordSum[i])
            info_list.append(dataOri.dispAdvice[i])
            info_list.append(dataOri.patientAge[i])
            info_list.append(dataOri.type[i])
            info_list.append(dataOri.patientVote[i])
            info_list.append(dataOri.onlineCons[i])
        if pd.isnull(dataOri.askList[i]) == False and dataOri.askList[i] != 'nan' and dataOri.askList[i] != '0':
            ask_list.append(dataOri.askList[i])
        if pd.isnull(dataOri.answerList[i]) == False and dataOri.answerList[i] != 'nan' and dataOri.answerList[i] != '0':
            answer_list.append(dataOri.answerList[i])
        if pd.isnull(dataOri.checkInList[i]) == False and dataOri.checkInList[i] != 'nan' and dataOri.checkInList[i] != '0':
            checkin_list.append(dataOri.checkInList[i])

        if dataOri.loc[i+1,'num'] == 0:   
            temp = pd.DataFrame([[idx, last_mod, ask_list, answer_list, checkin_list, 
            info_list[0], 
            ...
            info_list[6]]], columns=dialogue.columns.values)
            dialogue = pd.concat([dialogue, temp], axis=0)
            #dialogue = dialogue.append(temp)
            ask_list, answer_list, checkin_list, info_list =list(), list(), list(), list()
            last_mod = ''
            idx += 1
        else:
            continue
    ...

    dialogue['lastMod'] = pd.to_datetime(dialogue['lastMod'].astype(str), format='%Y.%m.%d')
    #dialogue = dialogue.dropna()
    dialogue = dialogue.reset_index(drop=True)
    #dialogue = dialogue.drop(columns='num')
    return dialogue

try:
    dialogue = format(originalData)
    dialogue.to_csv('dialogue.csv')
except Exception as e:
    print("exception", e)
```
### Aligning
Timestamps selections are based on our full-course observations and contain items sampling the whole-course counseling which are recorded from Jan. 1st, 2018 to Dec. 15th, 2022. ID are aligned by eliminating blank samples and obvious contradictory ones with inconsistent user complaints and interactions contents are removed.
```python
# chronic_temp_X1
dateStr5 = dt.strptime('2020-01-01', '%Y-%m-%d')
dateStr6 = dt.strptime('2021-01-01', '%Y-%m-%d')
# chronic_temp_X1
dateStr7 = dt.strptime('2021-01-01', '%Y-%m-%d')
dateStr8 = dt.strptime('2022-01-01', '%Y-%m-%d')
selected_condition3 = (pd.to_datetime(originalData.lastMod) >= dateStr5)&(pd.to_datetime(originalData.lastMod) <= dateStr6)
selected_condition4 = (pd.to_datetime(originalData.lastMod) >= dateStr7)&(pd.to_datetime(originalData.lastMod) <= dateStr8)

snsCondition3 = dialog.askLagTotal.values > 365
snsCondition4 = dialog.answerLagTotal.values > 365
dialog = dialog.drop(dialog[(snsCondition3)|(snsCondition4)].index)
```
### Filtering
Keep items with proper sentence lengths and eliminate ones with extreme short sentence, remove the items with abnormal, maximum and minimum values.
```python
textText.text_length.quantile(0.1)
textText = textText[textText['text_length'] > 1]
textText = textText[textText['text_length'] <= 250]
```
### Segmentation
Segmentation. Sentence-level segmented contents are reframed by Jieba toolkit, then the numbers and punctuation marks of the content are eliminated, and remaining tokenized texts are formatted, which retains only the adverbs, adjectives, and entities including information about the counseling and counseling quality in medical specialty.
### Stopwords
Chinese stop words (for Chinese reviews using the Harbin Institute of Technology list), context-specific stop words such as the name of the structured instructive words, and platform-specific words were excluded.
```python
stopWordFile = 'stopwords/stopwordsMerged.txt'
textText = pd.read_csv('textFile/recordText.txt', dtype=object)
my_stopwords =  [i.strip() for i in open(stopWordFile, encoding='utf-8').readlines()]
textText['text_length'] = 0
textText['text_length'] = textText['record'].apply(lambda x:len(str(x)))
#textText = textText[['review_seg']].replace('nan', ' ')
#complain
#advice
textText['record'] = textText['record'].astype(str)
textText['review_seg'] = textText['record'].apply(lambda x : ' '.join([j.strip() for j in jieba.lcut(x) if j not in my_stopwords]))
```
### Diagnosis-oriented embedding 
1)	For medical-domain-specific texts, we stem and lemmatize keywords generating groups to include effective clusters.
```python
ind_chronic = list(textText.loc[textText['review_seg'].str.contains(pattern)]['index'])
chronicdata = textText[[i in ind_chronic for i in textText['index']]]
chronicdata.to_csv("Record.csv", index = False, encoding = 'utf-8')
chronicItem = X.iloc[[int(i) for i in ind_chronic],:]
chronicItem.to_csv('RecordItem.csv')
```
2)	Clusterings are refined with various dimensionality reduction parameters by BERTopic models. Chronic items with top-ranked topics are selected with the best ranking of compact variety.
```python
model = SentenceTransformer('trueto/medbert-base-chinese')
## trueto/medalbert-base-wwm-chinese
## trueto/medalbert-base-chinese
# trueto/medbert-kd-chinese
# trueto/medbert-base-chinese
embeddings = model.encode(chronicdata['review_seg'].tolist(), show_progress_bar=True)
sys.setrecursionlimit(1000000)
umap_embeddings = umap.UMAP(n_neighbors=25,
                            n_components=10,
                            min_dist=0.00,
                            metric='cosine',
                            random_state=2020).fit_transform(embeddings)
cluster = hdbscan.HDBSCAN(min_cluster_size=30,
                          metric='euclidean',
                          cluster_selection_method='eom', 
                          prediction_data=True).fit(umap_embeddings)
umap_data = umap.UMAP(n_neighbors=15, 
                      n_components=2, 
                      min_dist=0.0,
                      metric='cosine').fit_transform(embeddings)
```
3)	Consequently, keywords are ranked in each group in terms of each chronic condition. Top segmentations of keywords are extracted to match the related corpus in each sample. Mismatched items of weak significance with low ranking are excluded.
```python
def extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=20):
    words = count.get_feature_names()
    labels = list(docs_per_topic.Topic)
    tf_idf_transposed = tf_idf.T
    indices = tf_idf_transposed.argsort()[:, -n:]
    top_n_words = {label: [(words[j], tf_idf_transposed[i][j]) for j in indices[i]][::-1] for i, label in enumerate(labels)}
    return top_n_words
```
## Dataframe Column Details

<class 'pandas.core.frame.DataFrame'>  

Int64Index: 383278 entries, 0 to 383277  

Data columns (total 32 columns):  

| #   | Column         | Non-Null Count  | Dtype   |   |
|-----|----------------|-----------------|---------|---|
| --- | ------         | --------------  | -----   |   |
| 0   | index          | 383278 non-null | int64   |   |
| 1   | lastMod        | 383278 non-null | object  |   |
| 2   | askList        | 381038 non-null | object  |   |
| 3   | answerList     | 383269 non-null | object  |   |
| 4   | checkInList    | 383278 non-null | object  |   |
| 5   | complaint      | 383277 non-null | object  |   |
| 6   | record         | 346164 non-null | object  |   |
| 7   | advice         | 347277 non-null | object  |   |
| 8   | consultingType | 383278 non-null | object  |   |
| 9   | patientVote    | 383278 non-null | object  |   |
| 10  | onlineCons     | 383278 non-null | object  |   |
| 11  | askLagTotal    | 383278 non-null | int64   |   |
| 12  | answerLagTotal | 383278 non-null | int64   |   |
| 13  | checkInLag     | 383273 non-null | object  |   |
| 14  | checkInTitle   | 383273 non-null | object  |   |
| 15  | checkInType    | 383273 non-null | object  |   |
| 16  | withOffLine    | 383278 non-null | int64   |   |
| 17  | timesCheckIn   | 383278 non-null | int64   |   |
| 18  | askFreq        | 383278 non-null | int64   |   |
| 19  | answerFreq     | 383278 non-null | int64   |   |
| 20  | checkInFreq    | 383278 non-null | int64   |   |
| 21  | satisficing    | 383278 non-null | float64 |   |
| 22  | lookBackType1  | 133083 non-null | object  |   |
| 23  | lookBackLag1   | 133182 non-null | float64 |   |
| 24  | lookBackType2  | 42037 non-null  | object  |   |
| 25  | lookBackLag2   | 42057 non-null  | float64 |   |
| 26  | lookBackType3  | 19595 non-null  | object  |   |
| 27  | lookBackLag3   | 19605 non-null  | float64 |   |
| 28  | lookAheadType  | 198803 non-null | object  |   |
| 29  | lookAheadLag   | 198803 non-null | float64 |   |
| 30  | patientSex     | 383278 non-null | object  |   |
| 31  | patientAge     | 383207 non-null | float64 |   |

dtypes: float64(6), int64(8), object(18)  

memory usage: 96.5+ MB  

