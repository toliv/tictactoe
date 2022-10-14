# Tic-Tac-Toe

## Setup

The service is Dockerized. Install Docker Desktop, then build and start the service by running `docker-compose up`. Validate that you can access the local server by visiting via browser or issuing a `GET` request to

http://localhost:5000/

You should be able to see a simple page showing a json
```json
{
    "tic_tac": "toe"
}
```

## Using the API

### Users

Users in Tic-Tac-Toe are unique individuals that may play in any number of games simultaneously.

User objects are simple and have shape

```json
{
    "id": str
}
```

A user can be created by sending a `POST` request to `/users`
A user can be fetched by sending a `GET` request to `/users/{id}`

### Games

Games in Tic-Tac-Toe are individual games that have shape
```json
{
    "id" : str,
    "status" : "pending_players"|"in_progress"|"completed",
    "board" : [[]], // an NxN matrix with Xs and Os where moves have occurred
    "players": [str], // a list of user id's playing in the game
    "results" : [GameResult] // a list of GameResult objects (described below)
}
```

A GameResult has shape
```json
{
    "user_id": str,
    "result" : "win"|"loss"|"tie"
}
```

#### The Game Lifecycle

Games proceed in their lifecycle, communicated by status.

A game that has not yet had enough players join has a status of `pending_players`

A game that is ready for a player to make a move (including the first move) has a status of `in_progress`

A game that has reached a terminal state has a status of `completed`.

#### Joining a Game

To join a game, make a `POST` request to `/games/{game_id}/join` with body
```json
{
    "user_id": str   
}
```

The response will contain a Game reflecting the user having joined the game. 

### Making a Move

To make a move on a game that is `in_progress`, make a `POST` request to `/games/{game_id}/move` with body
```json
{
    "user_id": str,
    "row" : str,
    "column": str
}

The response will contain a Game reflecting the move. 