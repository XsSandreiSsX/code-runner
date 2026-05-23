# XsSandreiSsX Dev Journal

## Patch 1.0:
I started this project because I’m planning to build projects such as an educational platform and a Codeforces-like website. I would also like to try connecting two services together. I also really wanted to work with such an amazing framework as FastAPI and get hands-on experience with it.

I also want to build workers that will run user submissions. This will be my first time working with tools like Celery, and honestly, I’m a little nervous about the final result

I’m also very interested in implementing a system for testing user submissions and taking protection against malicious code seriously.

<img src="https://assets.stickerswiki.app/s/a1955543499_by_kurumi_0bot/34ef8753.webp" width=128 height=128 alt="Am I tsundere? Not at all a fool">

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