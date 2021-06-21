using CSV, DataFrames, CategoricalArrays, Statistics, Chain, Dates
using Plots, StatsPlots
gr(dpi=300)

date_format = DateFormat("y-m-d H:M:S")

df =  CSV.read("data/flu_pt_raw_tweets.csv", DataFrame;
               header=["index", "id", "created_at", "text", "user",
                       "place", "user_place", "country", "coordinates",
                       "undefined_col", "undefined_col2", "undefined_col3"],
               types=[Int, Int, DateTime, String, Int,
                      String, String, String, String,
                      String, Int, Int],
                dateformat=date_format)


println(describe(df))

# filter!(:created_at => <(Dates.DateTime(2021), df)

# Total Tweets per day
gdf = @chain df begin
    transform(:created_at => ByRow(Dates.Date) => :created_at)
    groupby(:created_at)
end

tweet_plot = @df combine(gdf, nrow) plot(:created_at,
                            :nrow,
                            label=false,
                            xlabel="Day",
                            ylabel="Total Tweets Scraped",
                            yformatter=y -> string(round(Int64, y ÷ 1_000)) * "K",
                            xrotation=45)

savefig(tweet_plot, "images/tweets_scraped.png")

# Twitter Predictions
tweets_pred = CSV.read("data/tweets_pred.csv", DataFrame)
tweets_pred_plot = @df tweets_pred plot(:date,
                            :predicted,
                            label=false,
                            xlabel="Day",
                            ylabel="Total Tweets Predicted",
                            yformatter=y -> string(round(Int64, y ÷ 1_000)) * "K",
                            xrotation=45)
savefig(tweet_plot, "images/tweets_predicted.png")

# caso full here: https://data.brasil.io/dataset/covid19/caso_full.csv.gz
cases_br = @chain CSV.read("data/caso_full.csv", DataFrame) begin
    filter([:date, :city] => (date, city) -> date < Dates.Date("2021-01-01") && date > Dates.Date("2020-04-01") && ismissing(city), _)
    groupby(:date)
    combine(
        [:estimated_population_2019,
         :last_available_confirmed_per_100k_inhabitants,
         :last_available_deaths,
         :new_confirmed,
         :new_deaths] .=> sum .=>
         [:estimated_population_2019,
         :last_available_confirmed_per_100k_inhabitants,
         :last_available_deaths,
         :new_confirmed,
         :new_deaths]
    )
end

brazil_covid = @df cases_br plot(:date,
                            :last_available_deaths,
                            label="Total Deaths",
                            xlabel="Day",
                            legend=:topleft,
                            # ylabel="Total Tweets Predicted",
                            yformatter=y -> string(round(Int64, y ÷ 1_000)) * "K",
                            xrotation=45)
@df cases_br plot!(brazil_covid, :date, :new_confirmed, label="Daily Confirmed Cases")
savefig(brazil_covid, "images/brazil_2020.png")
