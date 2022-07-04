<h2>Books Reddit is Talking About</h2>
The goal of this project was to mine the Reddit r/books sub for the reads that prompted the most people to start a conversation so far in 2022, and understand, at scale, general feelings around the book. The technology stack consists of Elasticsearch, for storage, Spark and Textblob for analysis, and Google Sheets for the visualization. It utilizes the Openlibrary (https://openlibrary.org/developers/dumps) data dump for book titles, and the pushshift API to gather Reddit data.
The following viz is the result of the analysis, and below is the technology used in the process.

![reddit_books_viz](https://user-images.githubusercontent.com/11822655/177212612-6896c4df-d38d-4c8b-bc7b-fc367f44c2db.PNG)


<b>Data Gathering</b><br>
The idea behind this project was to parse book titles out of the post headers from the r/books subreddit. This ended up being quite challenging without employing a machine learned strategy (see next steps), and did ultimately require manual intervention to reach the final result, however, I learned a lot about Elasticsearch, NoSQL DBs, Spark, and Python along the way which was the primary goal.

 <b>The final pipeline architecture</b><br>
First, I bulk loaded the Openlibrary data dump (with X number of books) into elasticsearch. In order to keep the data small (all of this was running locally) I first pulled out the titles from the openlib dataset and dropped the authors, metadata, etc.

I then pulled about 6 months worth of r/books (~15k files dated back to the end of 2021)  from the pushshift.io API and dumped them into a CSV. I used pushshift, a site that aggregates and analyzes social media data, because Reddit has pretty strict rate limits on how many submissions you can pull.

<b>Mining for book names</b><br>
I ended up chunking the post titles into potential book titles (inspired by a similar project on Hacker News:https://towardsdatascience.com/hacker-news-book-suggestions-64b88099947
 ). Breaking the Reddit post title in blocks of sizes 2-6 and fuzzy searching my Elasticsearch book title database. The pro of this strategy was that there were few false negatives. If there was a book title in a post, it would be surfaced in the search. 
The problem was of course the false positives. As it is easy to see in the Python Notebook, the top 10 titles in the dataset were just random phrases that matched books in the Openlib dataset. 
This is where I ended up going through the grouped and counted titles to pull out the top 10.

<b>Analysis</b><br>
I read the full dataset (posts, descriptions, the book titles the script found) from a csv into Spark to do some basic counting and grouping to find the top titles. I then filtered my dataframe for those titles and used Textblob to get the positive/negative sentiment of the post.

Interestingly, ‘A Little Life’ by Hanya Yanagihara was the most posted about book and feelings were pretty mixed (about a third of comments were negative). Although I haven’t read the book, from what I’ve heard, it is a difficult read and I can understand why people would want to talk about it with others after finishing it. The theme continues with some others on the list that are known to be disturbing reads (American Psycho, Blood Meridian, even Fahrenheit 451 and The Secret History). So maybe the key to fiction writing is to deeply disturb but also entertain? Well maybe not the key, but at least it will get people talking.
Other books on the list were well expected; the Wheel of Time series is likely gaining more attention due to the 2021 TV show and books like Count of Monte Cristo and East of Eden will likely always spark discussion.




<b>Next steps</b><br>
This was a fun analysis to do, however there are many improvements I would love to make in the future. 
In order to make this an actual product the title mining would need to be fully automated. There are great options for training neural nets, and this project would be a great assist to manually tagging a training dataset. It would also be worth exploring further brute force text matching options, adding another layer of matching potential book titles against the text of the post titles or something along those lines
This ultimately would be much cooler if there was more data, however the book title search was slow going on my laptop. A V2 would take advantage of the cloud to actually run the various scripts on multiple nodes and expand the data collection and speed up the book title searches
There are many fantastic book subs (fantasy focused, scifi, etc). Further automation would allow this to expand
Further general analysis would also be interesting (What book discussion submissions sparked the longest conversations? How have top books changed over time? etc)



Links and tutorials</b><br>
Base script for pulling posts from pushshift: https://github.com/Watchful1/Sketchpad/blob/master/postDownloader.py
