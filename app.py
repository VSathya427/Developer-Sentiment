from flask import Flask, render_template, request
import pandas as pd
from pymongo import MongoClient
import plotly.graph_objects as go
import plotly.express as px


app = Flask(__name__)

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "databaseSystems"
COLLECTION_NAME = "project2"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

@app.route('/', methods=['GET', 'POST'])
def index():
    pipeline = [
        {
            "$project": {
                "SOAI": 1,
                "Age": 1,
                "YearsCodePro": 1,
                "sentiment": {
                    "$switch": {
                        "branches": [
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"happy|excited|good|sure|fine|agree|positive|great" } }, "then": "AI" },
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"sad|unhappy|negative|nothing|don't|disagree|dont" } }, "then": "NoAI" },
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"neutral|okay|ok" } }, "then": "neutral" }
                        ],
                        "default": "unknown"
                    }
                }
            }
        },
        {
            "$match": {
                "sentiment": {"$ne": "unknown"},
                "Age": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": {
                    "Age": "$Age",
                    "sentiment": "$sentiment"
                },
                "count": {"$sum": 1},
                "AvgYearsCode": {"$avg": "$YearsCodePro"}
            }
        },
        {
            "$group": {
                "_id": "$_id.Age",
                "sentiments": {
                    "$push": {
                        "sentiment": "$_id.sentiment",
                        "count": "$count",
                        "percentage": {"$divide": ["$count", {"$sum": "$count"}]},
                        "AvgYearsCode": "$AvgYearsCode"
                    }
                },
                "totalCount": {"$sum": "$count"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "Age": "$_id",
                "sentiments": {
                    "$map": {
                        "input": "$sentiments",
                        "as": "item",
                        "in": {
                            "sentiment": "$$item.sentiment",
                            "count": "$$item.count",
                            "percentage": {"$divide": ["$$item.count", {"$sum": "$sentiments.count"}]},
                            "AvgYearsCode": "$$item.AvgYearsCode"
                        }
                    }
                }
            }
        }
    ]

    # Perform the aggregation pipeline to retrieve the data
    pipeline1 = [
        {
            "$project": {
                "SOAI": 1,
                "sentiment": {
                    "$switch": {
                        "branches": [
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"happy|excited|good|sure|fine|agree|positive|great" } }, "then": "wanto" },
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"sad|unhappy|negative|nothing|don't|disagree|dont" } }, "then": "dontwantto" },
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"neutral|okay|ok" } }, "then": "neutral" }
                        ],
                        "default": "unknown"
                    }
                },
                "nationType": {
                    "$cond": {
                        "if": {"$in": ["$Country", ["United States of America", "Canada", "United Kingdom of Great Britain and Northern Ireland", "Germany", "Japan", "France", "Italy", "Australia", "South Korea", "Spain", "Netherlands", "Switzerland", "Sweden", "Belgium", "Austria", "Norway", "Denmark", "Finland", "Singapore", "Hong Kong", "Ireland", "New Zealand"]]},
                        "then": "Developed",
                        "else": "Developing"
                    }
                },
                "currency": "$Currency"
            }
        },
        {
            "$match": {
                "sentiment": {"$ne": "unknown"}
            }
        },
        {
            "$group": {
                "_id": {
                    "sentiment": "$sentiment",
                    "nationType": "$nationType",
                    "currency": "$currency"
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": {
                    "nationType": "$_id.nationType",
                    "currency": "$_id.currency"
                },
                "sentiments": {
                    "$push": {
                        "sentiment": "$_id.sentiment",
                        "count": "$count"
                    }
                },
                "totalCount": {"$sum": "$count"}
            }
        },
        {
            "$sort": {"totalCount": -1}
        },
        {
            "$group": {
                "_id": "$_id.nationType",
                "currencies": {
                    "$push": {
                        "currency": "$_id.currency",
                        "totalCount": "$totalCount"
                    }
                },
                "sentiments": {
                    "$first": {
                        "$map": {
                            "input": "$sentiments",
                            "as": "item",
                            "in": {
                                "sentiment": "$$item.sentiment",
                                "count": "$$item.count",
                                "percentage": {"$divide": ["$$item.count", "$totalCount"]}
                            }
                        }
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "nationType": "$_id",
                "mostUsedCurrency": {
                    "$cond": {
                        "if": {"$eq": [{"$arrayElemAt": ["$currencies.currency", 0]}, "NA"]},
                        "then": {"$arrayElemAt": ["$currencies.currency", 1]},
                        "else": {"$arrayElemAt": ["$currencies.currency", 0]}
                    }
                },
                "sentiments": 1
            }
        }
    ]


    # Perform the second aggregation pipeline to retrieve the data
    pipeline2 = [
        {
            "$project": {
                "SOAI": 1,
                "CompTotal": {
                    "$cond": {
                        "if": {"$and": [
                            {"$isNumber": "$CompTotal"},
                            {"$gt": ["$CompTotal", 0]}
                        ]},
                        "then": "$CompTotal",
                        "else": None
                    }
                },
                "DevType": 1,
                "YearsCodePro": 1,
                "Employment": 1,
                "sentiment": {
                    "$switch": {
                        "branches": [
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"happy|excited|good|sure|fine|agree|positive|great" } }, "then": "wanto" },
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"sad|unhappy|negative|nothing|don't|disagree|dont" } }, "then": "dontwantto" },
                            { "case": { "$regexMatch": { "input": { "$toString": "$SOAI" }, "regex": r"neutral|okay|ok" } }, "then": "neutral" }
                        ],
                        "default": "unknown"
                    }
                }
            }
        },
        {
            "$match": {
                "sentiment": { "$ne": "unknown" },
                "CompTotal": { "$ne": None }
            }
        },
        {
            "$group": {
                "_id": {
                    "DevType": "$DevType",
                    "CompBracket": {
                        "$cond": [
                            {"$lt": ["$CompTotal", 10000]}, "< 10000",
                            {"$cond": [
                                {"$and": [{"$gte": ["$CompTotal", 10000]}, {"$lt": ["$CompTotal", 100000]}]}, "10000 - 100000",
                                {"$cond": [
                                    {"$and": [{"$gte": ["$CompTotal", 100000]}, {"$lt": ["$CompTotal", 500000]}]}, "100000 - 500000",
                                    {"$cond": [
                                        {"$and": [{"$gte": ["$CompTotal", 500000]}, {"$lt": ["$CompTotal", 1000000]}]}, "500000 - 1000000",
                                        "> 1000000"
                                    ]}
                                ]}
                            ]}
                        ]
                    }
                },
                "wanto": {"$sum": {"$cond": [{"$eq": ["$sentiment", "wanto"]}, 1, 0]}},
                "dontwantto": {"$sum": {"$cond": [{"$eq": ["$sentiment", "dontwantto"]}, 1, 0]}},
                "neutral": {"$sum": {"$cond": [{"$eq": ["$sentiment", "neutral"]}, 1, 0]}},
                "AvgYearsCodePro": {"$avg": "$YearsCodePro"},
                "Employment": {"$push": "$Employment"}
            }
        },
        {
            "$addFields": {
                "totalSentiments": {"$sum": ["$wanto", "$dontwantto", "$neutral"]},
                "wantoPerc": {"$divide": ["$wanto", {"$sum": ["$wanto", "$dontwantto", "$neutral"]}]},
                "dontwantoPerc": {"$divide": ["$dontwantto", {"$sum": ["$wanto", "$dontwantto", "$neutral"]}]},
                "neutralPerc": {"$divide": ["$neutral", {"$sum": ["$wanto", "$dontwantto", "$neutral"]}]},
                "empPerc": {
                    "$map": {
                        "input": ["Employed full-time", "Self-employed", "Employed part-time", "Unemployed", "Student", "Retired", "Other"],
                        "as": "emp",
                        "in": {
                            "emp": "$$emp",
                            "perc": {"$divide": [{"$size": {"$filter": {"input": "$Employment", "as": "e", "cond": {"$eq": ["$$e", "$$emp"]}}}}, {"$size": "$Employment"}]}
                        }
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "DevType": "$_id.DevType",
                "CompBracket": "$_id.CompBracket",
                "wantoPerc": {"$round": ["$wantoPerc", 2]},
                "dontwantoPerc": {"$round": ["$dontwantoPerc", 2]},
                "neutralPerc": {"$round": ["$neutralPerc", 2]},
                "AvgYearsCodePro": 1,
                "empPerc": 1
            }
        }
    ]


    data = list(collection.aggregate(pipeline))
    data1 = list(collection.aggregate(pipeline1))
    data2 = list(collection.aggregate(pipeline2))


    fig = go.Figure()
    #sentiment_colors = {"AI": "limegreen", "NoAI": "coral", "neutral": "plum"}
    sentiment_colors = {"AI": "#ADD8E6", "NoAI": "#FFB6C1", "neutral": "#CCFFCC", "positive":"#FFC6C2","negative":"#C3E0DD"}


    for age_data in data:
        age = age_data["Age"]
        sentiments = age_data["sentiments"]
        for sentiment in sentiments:
            avg_years_code = sentiment['AvgYearsCode']
            fig.add_trace(go.Bar(
                name=f"{age} - {sentiment['sentiment']}",
                x=[age],
                y=[sentiment['percentage']],
                text=[f"{sentiment['percentage']*100:.2f}%"],
                hovertemplate=f"Age Group: {age}<br>Sentiment: {sentiment['sentiment']}<br>Percentage: {sentiment['percentage']*100:.2f}%<br>Average Years of Code: {avg_years_code:.2f} years",
                textposition='auto',
                marker_color=sentiment_colors[sentiment['sentiment']]
            ))

    fig.update_layout(
        title='Sentiment Comparison by Age Group',
        xaxis_title='Age Group',
        yaxis_title='Percentage',
        barmode='stack',
        showlegend=False 
    )
    plot_div = fig.to_html(full_html=False)





    # Create the visualization
    color_sequence = ['#ff8989', '#b19cd9']


    fig1 = go.Figure(data=[
        go.Bar(
            name='Developing',
            x=[item["sentiment"] for item in data1[0]["sentiments"]],
            y=[item["percentage"] for item in data1[0]["sentiments"]],
            marker_color=color_sequence[0],
            hovertemplate='Sentiment: %{x}<br>Percentage: %{y:.2%}<br>Most Used Currency: %{customdata}<extra></extra>',
            customdata=[data1[0]["mostUsedCurrency"]] * len(data1[0]["sentiments"])
        ),
        go.Bar(
            name='Developed',
            x=[item["sentiment"] for item in data1[1]["sentiments"]],
            y=[item["percentage"] for item in data1[1]["sentiments"]],
            marker_color=color_sequence[1],
            hovertemplate='Sentiment: %{x}<br>Percentage: %{y:.2%}<br>Most Used Currency: %{customdata}<extra></extra>',
            customdata=[data1[1]["mostUsedCurrency"]] * len(data1[1]["sentiments"])
        )
    ])

    fig1.update_layout(
        title='Sentiment Comparison between Developed and Developing Nations',
        xaxis_title='Sentiment',
        yaxis_title='Percentage',
        barmode='group'
    )

    plot_div1 = fig1.to_html(full_html=False)

    # Bubble chart for the second query
    # Create a DataFrame from data2
    df2 = pd.DataFrame(data2)

    # Filter out rows with 0 percent values
    df2 = df2[(df2["wantoPerc"] != 0) & (df2["dontwantoPerc"] != 0)]

    color_sequence2 = ['#ff8989', '#b19cd9']

    # Bubble chart using Plotly Express
    fig2 = px.scatter(df2, x="wantoPerc", y="dontwantoPerc", color="DevType",
                      hover_name="DevType",
                      hover_data=["CompBracket"],
                      title="Sentiment and Compensation Relationship by Developer Type",
                      labels={"wantoPerc": "Wanto %", "dontwantoPerc": "Dontwantto %"},
                      size="AvgYearsCodePro",  # Specify the size field
                      height=700,
                      width=900)

    plot_div2 = fig2.to_html(full_html=False)


    if request.method == 'POST':
        technology_type = request.form['technology']
        pipeline3 = [
            {
                "$project": {
                    "SOAI": 1,
                    "technology_type": {"$split": [f"${technology_type}", ";"]},
                    "sentiment": {
                        "$switch": {
                            "branches": [
                                {"case": {"$regexMatch": {"input": {"$toString": "$SOAI"}, "regex": "/happy|excited|good|sure|fine|agree|positive|great/i"}}, "then": "positive"},
                                {"case": {"$regexMatch": {"input": {"$toString": "$SOAI"}, "regex": "/sad|unhappy|negative|nothing|don't|disagree|dont/i"}}, "then": "negative"},
                                {"case": {"$regexMatch": {"input": {"$toString": "$SOAI"}, "regex": "/neutral|okay|ok/i"}}, "then": "neutral"}
                            ],
                            "default": "unknown"
                        }
                    }
                }
            },
            {
                "$match": {"sentiment": {"$ne": "unknown"}}
            },
            {
                "$unwind": "$technology_type"
            },
            {
                "$group": {
                    "_id": {
                        "technology": "$technology_type",
                        "sentiment": "$sentiment"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": "$_id.technology",
                    "sentiments": {
                        "$push": {
                            "sentiment": "$_id.sentiment",
                            "count": "$count"
                        }
                    },
                    "total_count": {"$sum": "$count"}  
                }
            },
            {
                "$sort": {"total_count": 1}  
            },
            {
                "$project": {
                    "_id": 0,
                    "technology": "$_id",
                    "sentiments": {
                        "$map": {
                            "input": "$sentiments",
                            "as": "sentiment",
                            "in": {
                                "sentiment": "$$sentiment.sentiment",
                                "count": "$$sentiment.count",
                                "percentage": {"$divide": ["$$sentiment.count", "$total_count"]}  
                            }
                        }
                    },
                    "total_count": "$total_count"  
                }
            }
        ]

        data3 = list(collection.aggregate(pipeline3))

        # Create the visualization
        fig = go.Figure()


        for tech_data in data3:
            technology = tech_data["technology"]
            sentiments = tech_data["sentiments"]
            total_count = tech_data["total_count"]

            for sentiment in sentiments:
                fig.add_trace(go.Bar(
                    name=f"{technology} - {sentiment['sentiment']}",
                    x=[sentiment['count']],
                    y=[technology],
                    text=[f"{sentiment['percentage']*100:.2f}%"],
                    textposition='auto',
                    marker_color=sentiment_colors[sentiment['sentiment']],
                    orientation='h'
                ))

        fig.update_layout(
            title=f'Sentiment Comparison by {technology_type}',
            xaxis_title='Count',
            yaxis_title=technology_type,
            barmode='stack',
            showlegend=False,
            height=800
        )

        plot_div3 = fig.to_html(full_html=False)

        return plot_div3



    return render_template("index.html",plot_div=plot_div ,plot_div1=plot_div1, plot_div2=plot_div2, plot_div3=None)

if __name__ == '__main__':
    app.run(debug=True)