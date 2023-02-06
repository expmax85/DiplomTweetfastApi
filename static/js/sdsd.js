async function handleSubmit() {
    const newTweetContent = {
        text: tweetContent.value.text,
        photos: tweetContent.value.imageList
    }
    const newTweet = new Tweet(new User(store.getters.getMe), newTweetContent);
    try {
        const mediaIds = [];

        const mediaUploads = tweetContent.value.imageList.map((image) => {
            const formData = new FormData();

            formData.append("file", image.file)

            return uploadMedia(formData);
        })

        const medias = await Promise.all(mediaUploads);

        medias.forEach(({data}) => mediaIds.push(data.media_id));

        newTweet.tweet_media_ids = mediaIds;

        await uploadTweet(newTweet);

        $notification({
            type: 'info',
            message: 'Твит отправлен!'
        })
    }
}