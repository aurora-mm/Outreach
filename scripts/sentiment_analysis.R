# Script for generating sentiment analysis plots

library(tidyverse)
library(tidytext)
library(tm)
library(wordcloud)
library(SnowballC)
library(textdata)
library(ggplot2)
library(udpipe)

post_directory <- "./posts"
post_files <- list.files(post_directory, full.names = TRUE)

# Read and concatenate all the content from the text files
all_posts <- post_files %>%
  map(readLines) %>%
  map_chr(paste, collapse = " ") %>%
  paste(collapse = " ")

# Load udpipe model
ud_model <- udpipe_download_model(language = "english")
udpipe_model <- udpipe_load_model(ud_model$file_model)

# Tokenize the text data
text_data <- tibble(text = all_posts)
words <- text_data %>%
  unnest_tokens(word, text)

# Load a sentiment lexicon for emotions (NRC)
emotion_lexicon <- get_sentiments("nrc")
emotion_words <- words %>%
  inner_join(emotion_lexicon, by = "word")

# Count emotion categories
emotion_count <- emotion_words %>%
  count(sentiment)

# Save bar plot of emotions as a PNG file
png("emotion_plot.png", width = 400, height = 400)
ggplot(emotion_count, aes(x = reorder(sentiment, n), y = n, fill = sentiment)) +
  geom_bar(stat = "identity", show.legend = FALSE, fill="steelblue") +
  coord_flip() +
  labs(title = "Emotions", x = "Emotion", y = "Word Count") +
  theme_minimal()
dev.off()

# Apply POS tagging to the tokenized words
pos_tagged <- udpipe_annotate(udpipe_model, x = words$word)
pos_tagged_df <- as.data.frame(pos_tagged)

# Filter for nouns
nouns <- pos_tagged_df %>%
  filter(upos %in% c("NOUN", "PROPN"))

# Prepare nouns for word cloud
noun_words <- nouns %>% count(token, sort = TRUE)

# Generate the word cloud and save as PNG
set.seed(12345)
png("wordcloud.png", width = 400, height = 400)
wordcloud(
  words = noun_words$token,
  freq = noun_words$n,
  min.freq = 2, 
  colors = brewer.pal(8, "Dark2"),
  scale = c(3, 0.5),
  max.words = 100 
)
dev.off()

