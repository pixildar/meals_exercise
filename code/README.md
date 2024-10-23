# Your book review service

Develop the following service using a language of your choice between [Go, Python, PHP].
You're free to use any framework and library, but be prepared to have to explain your choices!

Make the service easy to run either using a script, a Dockerfile or writing the commands in a documentation file.
And make sure to write some tests!

## Instructions

We have included a simple compose file to make it easy to run some support services that you could need, but feel free
to change or use something else completely.

To use it you need to have Docker installed, then you can run:

```bash
docker compose up
```

In this project you must use and integrate some calls from the OpenLibrary API.

You can find more details here: [openlibrary.org](https://openlibrary.org/developers/api)

## Endpoints

### Search meals

```http
GET /search?{keywords}
```

- Search on OpenLibrary, give back the `work_id` (and whatever seems appropriate) of matches

### Submit review

```http
POST /review
```

```json
{
  "work_id": "",
  "review": "text",
  "score": 6
}
```

- Validation (check the work_id matches on openlibrary, score range, review characters)
- Save the request to give back a reference for async processing
- Save on DB the complete data (asynchronously, enrich the data via openlibrary with cover image, metadata, etc.)

### Get review and its status

```http
GET /review/{id}
```

Which should follow the following behaviour:

- 202 response code while it's still processing
- 200 response code and your enriched data when everything is ready

### Update review

```http
PUT /review/{id}
```

Allows to update the score and the review content.

### Delete review

```http
DELETE /review/{id}
```

Delete the given review.

## Miscellaneous

Feel free to add everything that's useful or necessary to write high quality code, such as: automatic tests, static code
analysis, coding standards automations, etc.
