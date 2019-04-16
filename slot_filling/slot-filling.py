"""
2019.4.16 edited by henry
添加天气、火车班次查询语义槽
"""

from hustNlp.algorithms.rule_base.NER_for_slot import main as NER
import re

pattern_weather = r"是(晴天|雨天)吗|" \
                  r"是(晴天|雨天)还是.{1,3}？?|" \
                  r"会不会(下雨|下雪|刮风)|" \
                  r"天气怎么样?？|" \
                  r"(下雨|下雪|刮风|晴天|降温|升温|很冷|很热)?吗|" \
                  r"(冷|热)不(冷|热)"

pattern_traffic_train = r".+(到|去).+的?(火车|动车|高铁|列车)票?|" \
                  r".*(火车|动车|高铁|列车)票?\b|"


def weather_match(sentence, domain="天气"):
    """
    天气匹配语义槽，使用ner识别地点LOC，使用正则表达式识别时间time，意图intent。
    :param sentence: 输入文本
    :param domain: 所属领域
    :return: 返回语义槽字典slot{'domain': , 'intent': , 'time': , 'loc': }
    """
    slot = {}
    slot["domain"] = domain

    if re.search(pattern_weather, sentence):  # 意图识别，可添加基于深度学习的意图识别模型进行判断
        slot["intent"] = "询问天气情况"

    pattern_time = r".?天|星期.?|(这|本|下)?周.?|.?月.?号"
    time0 = re.search(pattern_time, sentence)
    if time0:
        slot["time"] = time0.group()

    # ner预测地点LOC（type = list）
    ner0 = NER.evaluate_line1(sentence)
    slot["loc"] = ner0["LOC"]
    print(slot)
    return slot


def traffic_train_match(sentence, domain="交通出行", category="火车"):
    """
    火车出行匹配语义槽，使用ner识别出发地（source）和目的地（destination），
    使用正则表达式识别日期（date）和时间（time），意图（intent）
    :param sentence:输入文本
    :param domain:所属领域
    :param category:二级类别
    :return:返回语义槽字典slot{'domain': , 'category': , 'intent': , 'date': , 'time': , 'source': , 'destination': }
    """
    slot = {}
    slot["domain"] = domain + "-" + category

    type0 = {"火车": ['G', 'D', 'K'], "动车": "D", "高铁": "G", "普快列车": "K"}
    for keyword, train_type in type0.items():
        if keyword in sentence:
            slot["train_type"] = train_type

    # 中国传统节日及国际节日
    festival = ["春节", "元宵节", "社日结", "花朝节", "清明节", "端午节", "七夕节",
                "中秋节", "重阳节", "冬至节", "除夕", "劳动节", "五一", "国庆节"]
    # 明天晚上，今天上午
    # 星期三晚上
    # 十月五号中午
    # 11月5日早晨
    # 春节下午五点十分
    pattern_date = r".?天|" \
                   r"星期.?|" \
                   r"(这|本|下)?周.?|" \
                   r"[一二三四五六七八九十][一二]?月[一二三四五六七八九十][一二三四五六七八九十]?[一二三四五六七八九十]?号|" \
                   r"[1-9][0-2]?月[1-9][0-9]?(号|日)?|" \
                   r"(春节|元宵|社日|花朝|清明|端午|七夕|中秋|重阳|除夕|冬至|劳动|国庆)节?"

    date0 = re.search(pattern_date, sentence)
    if date0:
        slot["date"] = date0.group()

    # 十点半，九点十分，九点整
    # 九点零五， 九点五十一
    # 12点30分，10点半
    # 9点05，5点30
    pattern_time = r"(凌晨|早晨|上午|中午|下午|晚上)?[一二两三四五六七八九十][一二三四五六七八九十]?(点|时).*(分|半|整)|" \
                   r"(凌晨|早晨|上午|中午|下午|晚上)?[一二两三四五六七八九十][一二三四五六七八九十]?(点|时)[零一二三四五六七八九十]?[一二三四五六七八九十]?[一二三四五六七八九十]?|" \
                   r"(凌晨|早晨|上午|中午|下午|晚上)?[0-9][0-9]?(点|时|.|：|:).*(分|半|整)|" \
                   r"(凌晨|早晨|上午|中午|下午|晚上)?[0-9][0-9]?(点|时|.|：|:)[0-9]?[0-9]?"
    time0 = re.search(pattern_time, sentence)
    if time0:
        slot["time"] = time0.group()

    pattern_train_time = r".+(发车|出发|到站)时间|.+几点发车？?"
    pattern_train_frequency = r".+有哪些"
    if re.search(pattern_train_time, sentence):                                   # 意图识别，可添加基于深度学习的意图识别模型进行判断
        slot["intent"] = "询问列车时间"
    elif re.search(pattern_train_frequency, sentence):
        slot["intent"] = "查询列车班次"



    ner0 = NER.evaluate_line1(sentence)
    try:
        slot["source"] = ner0["LOC"][0]
        slot["destination"] = ner0["LOC"][1]
    except:
        print("目的地或出发地为空")
        pass
    print(slot)
    return slot


def slot_filling(sentence):

    if re.search(pattern_weather, sentence):    # domain判断
        weather_match(sentence)                 # 天气领域
    elif re.search(pattern_traffic_train, question):
        traffic_train_match(sentence)           # 交通出行领域—火车


if __name__ == '__main__':
    # question = "明天洛杉矶会不会下雪啊？"      # 天气相关

    # 十月三十一号凌晨两点十分从南京南开往上海虹桥的高铁
    question = "下周三下午六点零二从汉口开往深圳的动车"  # 交通出行-火车

    slot_filling(question)

    # a = re.search(r"下雪", sentence)           # aba
    # print(a.groups())