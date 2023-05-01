import pandas as pd
import numpy as np
from pyecharts.charts import *
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.components import Table
from pyecharts.faker import Faker
from pyecharts.globals import SymbolType, ThemeType
from pyecharts.options import ComponentTitleOpts
from dateutil import parser

hotel_data = pd.read_csv('data/hotel_bookings.csv')
# print(hotel_data.shape)
# print(hotel_data.head(5))

# hotel_data.info()
# print(hotel_data.isnull().sum()[hotel_data.isnull().sum() != 0])
hotel_data.drop('company', axis=1, inplace=True)
# hotel_data.info()
hotel_data_children = hotel_data.groupby(['children']).count()['hotel']
# print(hotel_data_children)
children = (
    Pie()
    .add("", [list(z) for z in zip(hotel_data_children.index.tolist(), hotel_data_children.values.tolist())])
    .set_global_opts(title_opts=opts.TitleOpts(title="儿童人数分布"))
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    .render("可视化结果/儿童人数分布.html")
)
# 使用众数填充
# print(hotel_data.mode())
hotel_data['children'].fillna(hotel_data['children'].mode()[0], inplace=True)
hotel_data['country'].fillna(hotel_data['country'].mode()[0], inplace=True)
hotel_data['agent'].fillna(0, inplace=True)

# print(hotel_data.duplicated(keep='first').sum())
hotel_data.drop_duplicates(keep='first', inplace=True)
# print(hotel_data.duplicated(keep='first').sum())

hotel_data['meal'] = hotel_data['meal'].str.replace('Undefined', 'SC')

hotel_list = list(hotel_data['adults'] + hotel_data['children'] + hotel_data['babies'] == 0)
hotel_data.drop(hotel_data.index[hotel_list], inplace=True)
# 将月份转化为阿拉伯数据便于观察
months = []
for m in hotel_data['arrival_date_month']:
    month = parser.parse(m).month
    months.append(month)
hotel_data['Month'] = months
# 对数据进行划分
hotel_City_data = hotel_data[(hotel_data['hotel'] == 'City Hotel') & (hotel_data['is_canceled'] == 0)]
# print(hotel_City_data.head(5))
hotel_Resort_data = hotel_data[(hotel_data['hotel'] == 'Resort Hotel') & (hotel_data['is_canceled'] == 0)]


# 不同酒店的预定数据量以及每个类型酒店的入住率
def hotel_count():
    HotelCount = hotel_data.groupby(['hotel'])['is_canceled'].count() \
        .reset_index().rename(columns={"is_canceled": "count"})
    print("两种类型的酒店预定情况\n", HotelCount)
    HotelCheck = hotel_data.groupby(['is_canceled', 'hotel']).count()['lead_time']
    print(HotelCheck)
    City_rate_0 = str(round(HotelCheck[0][0] / HotelCount['count'][0] * 100, 2)) + "%"
    print("类型为City的酒店入住率为", City_rate_0)
    Resort_rate_0 = str(round(HotelCheck[0][1] / HotelCount['count'][1] * 100, 2)) + "%"
    print("类型为Resort的酒店入住率为", Resort_rate_0)


# 分析时间维度的酒店的订单
def every_month():
    every_year_0 = hotel_data[hotel_data['is_canceled'] == 0].groupby('arrival_date_year').count()['hotel']
    every_year_1 = hotel_data[hotel_data['is_canceled'] == 1].groupby('arrival_date_year').count()['hotel']
    # print(every_year)
    (
        Bar()
        .add_xaxis(every_year_0.index.tolist())
        .add_yaxis("有效订单", every_year_0.values.tolist())
        .add_yaxis("无效订单", every_year_1.values.tolist())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="每一年的订单情况", subtitle="有效与退订"),
        )
        .render("可视化结果/每一年的订单情况.html")
    )
    # 每一年每一个月的有效订单变化
    EverMonth2015 = hotel_data[(hotel_data['arrival_date_year'] == 2015)
                               & (hotel_data['is_canceled'] == 0)].groupby(['Month']).count()['hotel']
    EverMonth2016 = hotel_data[(hotel_data['arrival_date_year'] == 2016)
                               & (hotel_data['is_canceled'] == 0)].groupby(['Month']).count()['hotel']
    EverMonth2017 = hotel_data[(hotel_data['arrival_date_year'] == 2017)
                               & (hotel_data['is_canceled'] == 0)].groupby(['Month']).count()['hotel']
    print(EverMonth2016.index.tolist())
    print(EverMonth2016.values.tolist())
    c = (
        Line()
        .add_xaxis(EverMonth2016.index.tolist())
        .add_yaxis("2016", EverMonth2016.values.tolist(), is_step=True)
        .add_yaxis("2015", EverMonth2015.values.tolist(), is_step=True)
        .add_yaxis("2017", EverMonth2017.values.tolist(), is_step=True)
        .set_global_opts(title_opts=opts.TitleOpts(title="每年每月有效订单"))
        .render("可视化结果/每年每月有效订单.html")
    )


# 分析受欢迎的房型
def hotel_room():
    hotel_data_room = hotel_data.groupby(['reserved_room_type']).count()['hotel']
    # print(hotel_data_room)
    c = (
        Bar()
        .add_xaxis(hotel_data_room.index.tolist())
        .add_yaxis("整体房型数量", hotel_data_room.values.tolist())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="整体房型数量"),
        )
        .render("可视化结果/整体房型数量.html")
    )
    # 不同酒店的房型预定情况
    hotel_room_stype_City = hotel_City_data.groupby('assigned_room_type')['hotel'].count() \
        .reset_index().rename(columns={"hotel": "room_counts"})
    hotel_room_stype_Resort = hotel_Resort_data.groupby('assigned_room_type')['hotel'].count() \
        .reset_index().rename(columns={"hotel": "room_counts"})
    # print(hotel_room_stype_City)
    c = (
        Bar()
        .add_xaxis(hotel_room_stype_City['assigned_room_type'].tolist())
        .add_yaxis("City", hotel_room_stype_City['room_counts'].tolist())
        .add_yaxis("Resort", hotel_room_stype_Resort['room_counts'].tolist())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="City-Resort类型房型"),
        )
        .render("可视化结果/City-Resort类型房型.html")
    )


# 不同类型酒店的复定情况
def hotel_repeat():
    # print(hotel_data.shape)
    print("所有酒店类型的复订率为:", str(round(hotel_data.groupby(['is_repeated_guest']).count()['hotel'][1]
                                               / hotel_data.count()[0] * 100, 2)) + "%")
    HotelRepeat = hotel_data.groupby(['hotel', 'is_repeated_guest']).count()['reserved_room_type']
    # print(HotelRepeat)
    print("City类型的复订率为:", str(round(HotelRepeat[1] / (HotelRepeat[0] + HotelRepeat[1]) * 100, 2)) + '%')
    print("Resort类型的复订率为:", str(round(HotelRepeat[3] / (HotelRepeat[2] + HotelRepeat[3]) * 100, 2)) + '%')


def season_hostel():
    # 使得每个月份映射成为季节
    season = {"January": "冬季", "February": "春季", "March": "春季", "April": "春季", "May": "夏季", "June": "夏季",
              "July": "夏季", "August": "秋季", "September": "秋季", "October": "秋季", "November": "冬季",
              "December": "冬季"}
    hotel_City_data["seasons"] = hotel_City_data["arrival_date_month"].map(season)
    hotel_Resort_data["seasons"] = hotel_Resort_data["arrival_date_month"].map(season)
    # 统计City类型的房屋订购情况
    hotel_City_Seasons = hotel_City_data.groupby(['seasons', 'reserved_room_type'])['hotel'].count()
    # print(hotel_City_Seasons)
    # print(hotel_City_Seasons['冬季'])
    # 统计Resort类型的房屋订购情况
    hotel_Resort_Seasons = hotel_Resort_data.groupby(['seasons', 'reserved_room_type'])['hotel'].count()
    # 分别绘制春夏秋冬四季的房屋订购情况柱状图
    c1 = (
        Bar()
        .add_xaxis(hotel_City_Seasons['春季'].index.tolist())
        .add_yaxis("City", hotel_City_Seasons['春季'].values.tolist())
        .add_yaxis("Resort", hotel_Resort_Seasons['春季'].values.tolist())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="City-Resort春季类型房型"),
        )
        .render("可视化结果/City-Resort春季类型房型.html")
    )
    c2 = (
        Bar()
        .add_xaxis(hotel_City_Seasons['夏季'].index.tolist())
        .add_yaxis("City", hotel_City_Seasons['夏季'].values.tolist())
        .add_yaxis("Resort", hotel_Resort_Seasons['夏季'].values.tolist())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="City-Resort夏季类型房型"),
        )
        .render("可视化结果/City-Resort夏季类型房型.html")
    )
    c3 = (
        Bar()
        .add_xaxis(hotel_City_Seasons['秋季'].index.tolist())
        .add_yaxis("City", hotel_City_Seasons['秋季'].values.tolist())
        .add_yaxis("Resort", hotel_Resort_Seasons['秋季'].values.tolist())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="City-Resort秋季类型房型"),
        )
        .render("可视化结果/City-Resort秋季类型房型.html")
    )
    c4 = (
        Bar()
        .add_xaxis(hotel_City_Seasons['冬季'].index.tolist())
        .add_yaxis("City", hotel_City_Seasons['冬季'].values.tolist())
        .add_yaxis("Resort", hotel_Resort_Seasons['冬季'].values.tolist())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            title_opts=opts.TitleOpts(title="City-Resort冬季类型房型"),
        )
        .render("可视化结果/City-Resort冬季类型房型.html")
    )


# 分析每个成功入住一周的天数
def hostel_stay():
    hotel_City_data['total_day'] = hotel_City_data['stays_in_week_nights'] \
                                   + hotel_City_data['stays_in_weekend_nights']
    hotel_Resort_data['total_day'] = hotel_Resort_data['stays_in_week_nights'] \
                                     + hotel_Resort_data['stays_in_weekend_nights']

    hotel_City_data_day = hotel_City_data.groupby('total_day')['stays_in_week_nights'].count()
    hotel_Resort_data_day = hotel_Resort_data.groupby('total_day')['stays_in_week_nights'].count()

    list_city = [list(z) for z in zip(hotel_City_data_day.index.tolist(), hotel_City_data_day.values.tolist())]
    list_resort = [list(z) for z in zip(hotel_Resort_data_day.index.tolist(), hotel_Resort_data_day.values.tolist())]
    table = Table()
    table2 = Table()
    headers = ["天数", "次数"]
    rows1 = list_city
    rows2 = list_resort
    table.add(headers, rows1)
    table.set_global_opts(
        title_opts=ComponentTitleOpts(title="city类型租住情况", subtitle="city类型租住情况")
    )
    table.render("可视化结果/city类型租住情况.html")
    table2.add(headers, rows2)
    table2.set_global_opts(
        title_opts=ComponentTitleOpts(title="resort类型租住情况")
    )
    table2.render("可视化结果/resort类型租住情况.html")


# 探索客户取消订单的因素
def Factor():
    data = hotel_data[['is_canceled', 'reserved_room_type', 'assigned_room_type']]
    data['equal'] = data.apply(lambda row: 1 if row['reserved_room_type']
                                                == row['assigned_room_type'] else 0, axis=1)
    print("在所有预定订单中1为预定与酒店保留房型相同0为不同")
    print('*' * 100)
    print(data['equal'].value_counts())
    # 探索取消订单的人中或许受预定房型不一的情况
    data_1 = data.groupby(['is_canceled', 'equal']).count()['reserved_room_type']
    print(data_1)
    c = (
        Pie()
        .add("", [list(z) for z in zip(data_1[1].index.tolist(), data_1.values.tolist())])
        .set_global_opts(title_opts=opts.TitleOpts(title="房型不不一占比"))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
        .render("可视化结果/取消订单中房型不不一占比.html")
    )
    # 结果为19%的人取消和房型有关


# 探索餐饮对订单退订的影响
def food():
    data_food = hotel_data[['is_canceled', 'meal']]
    data_food_0 = data_food[data_food['is_canceled'] == 0].groupby('meal').count()
    data_food_1 = data_food[data_food['is_canceled'] == 1].groupby('meal').count()

    (
        Pie()
        .add(
            "没有取消订单占比",
            [list(z) for z in zip(data_food_0.index.tolist(), data_food_0.values.tolist())],
            center=["20%", "30%"],
            radius=[60, 80],
        )
        .add(
            "取消订单占比",
            [list(z) for z in zip(data_food_1.index.tolist(), data_food_1.values.tolist())],
            center=["55%", "30%"],
            radius=[60, 80],

        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="订单取消与餐饮类型的关系"),
            legend_opts=opts.LegendOpts(
                type_="scroll", pos_top="20%", pos_left="80%", orient="vertical"
            ),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
        .render("可视化结果/订单取消与餐饮类型的关系.html")
    )


# 结果显示取消的与没有取消的比例分布大致相同,所以餐饮不是影响取消订单主要因素

# 从销售渠道的方面探索退订率
def distribution_channel():
    data_distribution = hotel_data.groupby('distribution_channel').count()['hotel']
    data = hotel_data.groupby(['distribution_channel', 'is_canceled']).count()['hotel']
    print(data_distribution)
    print(data)
    for x in data_distribution.index:
        print(f"{x}的退订率为:", str(round(data[x][1] / data_distribution[x], 2) * 100) + '%')


'''
结果:Undefined表示未知,且数量只有5个,不具有解释性,其余的渠道中,
TA/TO的退订率为31%,且订单的数量较多,不排除存在渠道的奖励机制,存在水分
'''

if __name__ == '__main__':
    # hotel_count()
    every_month()
    # hotel_room()
    # # hotel_repeat()
    # season_hostel()
    # hostel_stay()
    # Factor()
    # food()
    # distribution_channel()
