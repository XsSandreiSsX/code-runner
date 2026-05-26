# **XsSandreiSsX Dev Journal**

## Patch 1.0:
I started this project because I’m planning to build projects such as an educational platform and a Codeforces-like website. I would also like to try connecting two services together. I also really wanted to work with such an amazing framework as FastAPI and get hands-on experience with it.

I also want to build workers that will run user submissions. This will be my first time working with tools like Celery, and honestly, I’m a little nervous about the final result

I’m also very interested in implementing a system for testing user submissions and taking protection against malicious code seriously.

<img src="https://assets.stickerswiki.app/s/a1955543499_by_kurumi_0bot/34ef8753.webp" width=128 height=128 alt="Am I tsundere? Definitely not...">

### Planned Features
<ol>
    <li>Add database support</li>
    <li>Implement JWT authentication</li>
    <li>Create routers for managing test case system</li>
    <li>Add Celery workers for running user submissions</li>
    <li>Implement submission queue processing</li>
    <li>Add sandbox protection for malicious code</li>
</ol>

## Patch 1.1:
### Changelog
Added an environment file containing the basic project configuration.

Added a very important parameter: `DEBUG=True`. If it is enabled, the project uses a local SQLite database; otherwise, it uses PostgreSQL.

Right now, I’m following the idea that different services will use the code-runner and send user code for testing.

Because of this, I created a `Service` table where we can add services and automatically generate a random `jwt_secret`. This secret will be used by third-party services when sending requests to the code-runner as a small security measure. I will improve this logic further soon.

At the moment, I implemented CLI access for convenient service creation/removal, though I may change this approach in the future.

I also added custom exceptions that should help prevent accidental bugs on my side, but they should not affect the client side in any way. To this end I want to create separate `ClientExceptions`.

<img src="https://i.pinimg.com/1200x/d6/19/43/d619434bd9ca8da771f8c2666b53767b.jpg" width=128 height=128 alt="Я посмотрел финал The Boys">

### Future Features:
<ol>
    <li>I’m planning to implement JWT authorization logic.</li>
    <li>Add several endpoints for creating, deleting, and maybe updating test suites.</li>
    <li>I will also add separate client-side exceptions.</li>
    <li>I’m planning to add corresponding database models for test suites, test cases, and related entities.</li>
</ol>

## Patch 1.2: 
The core idea of the code-runner is that it should not know the problem title, for example “Add a+b”.
It also should not store submission history.

The code-runner should work like this:

“Here is the user solution.”
“Okay, I see it, I run the tests and return the result.”

That is where its logic ends. Of course, we also should not forget about time and memory limits.

A platform _like Codeforces_, on the other hand, stores submissions, attempt history, and the actual problem title.

Right now, I see it like this:
a ```test_suite``` is created inside the code-runner, and the website receives its id.

After that, when the user submits code, it sends something like ```/submit/```.
This means the code-runner stores the tests internally, and only the user solution is sent during submissions.

I also considered another approach where both the user solution and the entire test suite are sent in a single endpoint request.

However, let’s imagine an average problem with around 50 tests, and for example, a list containing 10^5 elements where ai <= 10^9.

That would be a huge amount of data transferred repeatedly, especially considering that a user may make multiple submission attempts after getting Wrong Answer.

### Changelog
Added a Pydantic `ClientResponse` schema to make responses from the code-runner consistent.

Added new models:
- `TestCase` — a model for a single test case.
- `TestSuite` — a model for a test suite.

`TestSuite` has a one-to-many relationship with `TestCase`.

Currently, we have:
- `time_limit`
- `memory_limit`
- a list of test cases

Added 4 endpoints:
- create a test suite
- get a test suite
- delete a test suite
- update a test suite

Also added several client-side exceptions and an `error_handler`, which guarantees that responses are returned in a consistent style.

Just look at how clean these endpoints are. I moved the business logic out of the endpoints into a separate class.

### Future Features
<ul>
  <li>Added a relationship between <code>TestSuite</code> and services, so each service only has access to its own test suites.</li>

  <li>Planning to finish JWT authorization and use it to protect all API methods.</li>

  <li>Added access control checks:
    <ul>
      <li><code>service_id</code> from JWT must match the owner of the <code>TestSuite</code></li>
      <li>services cannot get, update, or delete чужие test suites</li>
    </ul>
  </li>
</ul>