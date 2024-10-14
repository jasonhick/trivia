# Trivia API Documentation

## Introduction
The Trivia API provides endpoints for managing a trivia game, including fetching questions, categories, creating new questions, and playing quizzes.

## Base URL
The base URL for all endpoints is: `http://localhost:5000`

## Authentication
This version of the API does not require authentication.

## Error Handling
Errors are returned as JSON objects in the following format:


The API will return three error types when requests fail:   
- 400: Bad request  
- 404: Resource not found  
- 422: Unprocessable entity
- 500: Internal server error

```json
{
  "success": False,
  "error": 404,
  "message": "Resource not found"
}
```


## Endpoints

### GET /categories
Fetches a dictionary of all available categories.

- Request Arguments: None
- Returns: An object with keys:
  - `success`: Boolean indicating successful request
  - `categories`: An object of `id: category_string` key-value pairs

#### Example Response
```
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

### GET /questions
Fetches a list of questions, paginated in groups of 10.

- Request Arguments:
  - `page`: Integer for specifying the page number (default is 1)
- Returns: An object with keys:
  - `success`: Boolean indicating successful request
  - `questions`: A list of questions
  - `total_questions`: Total number of questions
  - `categories`: An object of `id: category_string` key-value pairs
  - `current_category`: The current category (default is None)

#### Example Response
```
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": 1,
      "difficulty": 1
    },
    {
      "id": 2,
      "question": "What is the largest planet in our solar system?",
      "answer": "Jupiter",
      "category": 2,
      "difficulty": 2
    }
  ],
  "total_questions": 20,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null
}
```

### POST /questions
Creates a new question.

- Request Body:
  - `question`: String containing the question text
  - `answer`: String containing the answer text
  - `category`: Integer for the category ID
  - `difficulty`: Integer for the difficulty level
- Returns: An object with keys:
  - `success`: Boolean indicating successful request
  - `created`: Integer ID of the created question

#### Example Request
```
{
  "question": "What is the capital of France?",
  "answer": "Paris",
  "category": 1,
  "difficulty": 1
}
```

#### Example Response
```
{
  "success": true,
  "created": 21
}
```

### DELETE /questions/<int:question_id>
Deletes a question by ID.

- Request Arguments:
  - `question_id`: Integer for the question ID
- Returns: An object with keys:
  - `success`: Boolean indicating successful request
  - `deleted`: Integer ID of the deleted question

#### Example Request
```
{
  "question_id": 21
}
```

#### Example Response
```
{
  "success": true,
  "deleted": 21
}
```

### POST /questions/search
Searches for questions based on a search term.

- Request Body:
  - `searchTerm`: String containing the search term
- Returns: An object with keys:
  - `success`: Boolean indicating successful request
  - `questions`: A list of questions
  - `total_questions`: Total number of questions
  - `current_category`: The current category (default is None)

#### Example Request
```
{
  "searchTerm": "capital"
}
```

#### Example Response
```
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": 1,
      "difficulty": 1
    }
  ],
  "total_questions": 1,
  "current_category": null
}
```

### GET /categories/<int:category_id>/questions
Fetches questions for a specific category.

- Request Arguments:
  - `category_id`: Integer for the category ID
- Returns: An object with keys:
  - `success`: Boolean indicating successful request
  - `questions`: A list of questions
  - `total_questions`: Total number of questions
  - `current_category`: The current category

#### Example Request
```
{
  "category_id": 1
}
```

#### Example Response
```
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": 1,
      "difficulty": 1
    }
  ],
  "total_questions": 1,
  "current_category": "Science"
}
```

### POST /quizzes
Plays a quiz based on the selected category and previous questions.

- Request Body:
  - `previous_questions`: List of integers for previously asked questions
  - `quiz_category`: Object containing the category ID and type
- Returns: An object with keys:
  - `success`: Boolean indicating successful request
  - `question`: An object containing the question details

#### Example Request
```
{
  "previous_questions": [1, 2],
  "quiz_category": {
    "id": 1,
    "type": "Science"
  }
}
```

#### Example Response
```
{
  "success": true,
  "question": {
    "id": 3,
    "question": "What is the capital of Japan?",
    "answer": "Tokyo",
    "category": 3,
    "difficulty": 3
  }
}
```
