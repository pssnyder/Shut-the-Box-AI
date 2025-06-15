# 🎲 Shut the Box Showdown: You, Robots & Super Smart AI! 🤖🧠

Hey, math whizzes and future game designers! 👋 Get ready to play "Shut the Box," a classic game of dice and strategy! But here's the cool part: you can play it, watch different robot players try their luck, AND even see a super-duper smart computer brain learn from *all* their games! 🤯

### What's "Shut the Box" All About? 🎯

Imagine you have a row of wooden tiles numbered 1 to 9. You roll two dice, and then you try to flip down (or "shut") tiles that add up to your dice roll. For example, if you roll a 7, you could shut the 7 tile, OR the 3 and 4 tiles, or even the 1 and 6 tiles! The goal is to shut as many tiles as you can. The lower your score at the end (because you couldn't shut any more tiles), the better! 🎉

This amazing project lets you:
* **Play the Game!** 🧑‍💻 Roll those digital dice and make your moves!
* **Watch Robot Players!** 🤖 See different computer "brains" try to win with their own special strategies.
* **Teach a Super-Brain!** 💡 Use *all* the robot games to train an even smarter AI to understand the game like never before!

## Awesome Things You'll Find Inside! ✨

* **The Game Machine (`shut_the_box.py`):** ⚙️ This is the heart of the game! It handles everything: rolling dice, flipping tiles, and making sure everyone plays fair. You can play it yourself, or let the robots take over!
* **Robot Playbooks! (Different AI Strategies in `shut_the_box.py`):** 🤖📖 We've given our robots different ways to "think" about playing the game. Which one do you think is smartest?
    * **The "Random Roller" (Strategy 0):** Just picks moves randomly, like closing your eyes and pointing! 🙈
    * **The "Single Seeker" (Strategy 1):** Tries to close just one tile if it matches the dice sum, or uses individual dice numbers. One and done! ✅
    * **The "Big Blocker" (Strategy 2):** Always tries to close the *most* tiles possible with one roll. Go big or go home! 💥
    * **The "Smart Guesser" (Strategy 3):** Looks at which numbers are *least* likely to be useful later and tries to get rid of them now. A real chess player! 🧐
    * **The "Inside Out" Thinker (Strategy 4):** Likes to close tiles closer to the middle of the board first. Keeping things neat! 🗄️
    * **The "Outside In" Adventurer (Strategy 5):** Goes for the tiles on the edges of the board first. Brave moves! 🏞️
* **Robot Practice Time! (Simulation Framework in `shut_the_box.py`):** 🏟️ This lets us make our robots play HUNDREDS or even THOUSANDS of games! It's like a huge practice tournament to see which playbook is best. All the scores get saved! 📊
* **Scoreboard Central! (`analyze_results.py`):** 📈 After all those robot games, this part helps us add up all the scores and see who the champion robot really is! It even makes cool charts and graphs! 🏆
* **The Super-Brain Trainer! (`train_deep_learning_model.py`):** 🧠💡 This is where the magic happens! We take *all* the saved games and use them to teach a special kind of AI called **Deep Learning**. It learns to spot hidden patterns and make super smart predictions, almost like it's learning to be a game expert by watching others play for a very long time! 🌟

## Let's Get Rolling! (Your Mission Starts Here!) 🚀

Ready to play and learn with AI? Here’s how to get everything set up!

### What You Need:

* **Python Power!** 🐍 Make sure you have Python 3 installed on your computer. (Ask a grown-up if you need help installing it!)
* **Special Tools!** 🔧 You'll need a few extra Python tools.
    ```bash
    pip install pandas matplotlib numpy torch
    ```

### Get Your Game Files!

1.  **Clone the Code!** (This is like getting all the game pieces!)
    ```bash
    git clone [https://github.com/your-username/shut-the-box-ai.git](https://github.com/your-username/shut-the-box-ai.git)
    cd shut-the-box-ai
    ```
2.  **Make Some Folders!** (These are like filing cabinets for your game results and robot brains!)
    ```bash
    mkdir -p logs results models
    ```

### How to Make Robots Play & See Their Scores! 🤖📊

1.  **Tell the Robots How to Play (`shut_the_box.py`):**
    * Open the `shut_the_box.py` file (use a text editor, like Notepad or VS Code).
    * Find where it says `NUM_GAMES` and decide how many games each robot should play (e.g., `100` for 100 games!).
    * Look for `STRATEGIES` to pick *which* robot playbooks you want to test (e.g., `[0,1,2]` for the first three robots, or `[0,1,2,3,4,5]` for all of them!).
    * Make sure `PLAY_TYPE = 1` is set (this means the AI robots will play).
    * Save the file!
2.  **Start the Robot Tournament!** 🏁
    ```bash
    python shut_the_box.py
    ```
    This will run all the games, and the scores will magically appear in the `./results/` folder!
3.  **Check the Scoreboard!** 🏆
    * Open `analyze_results.py`.
    * Pick which robots' scores you want to compare in the `strategies` list.
    * Run the analysis script:
        ```bash
        python analyze_results.py
        ```
    This will show you who won and even draw cool bar charts to compare them!

### How to Train the Super-Brain AI! 🧠💡

1.  **Make sure the Robots Played Lots!** 📈 You need to run `python shut_the_box.py` first to get lots of game data saved in `./results/`!
2.  **Tell the Super-Brain What to Learn From (`train_deep_learning_model.py`):**
    * Open `train_deep_learning_model.py`.
    * Find `TRAINING_FILE` and make sure it points to one of the JSON files from your robot games in `./results/`.
    * You can also tweak how long the brain trains (`EPOCHS`) or how fast it learns (`LEARNING_RATE`).
    * Save the file!
3.  **Start the Brain Training!** 🚀
    ```bash
    python train_deep_learning_model.py
    ```
    Watch it go! The super-smart brain will be saved in the `./models/` folder when it's done training!

## What's Next for Our Game? (Future Upgrades!) 🌟

We're always dreaming of making this project even more epic!

* **Even Smarter Robots!** 🤖 We want to teach our AI players even *more* amazing ways to play Shut the Box, like grandmasters!
* **Better Brain Training!** 🧠 We'll make our super-brain even better at learning and predicting game outcomes.
* **Cool Pictures & Buttons!** 🎨 Imagine playing with a beautiful, colorful game board with buttons you can click! We want to build a graphical version.
* **AI vs. AI Tournaments!** 🥊 Maybe we can make the AI robots play against each other to see who's truly the best!

## Want to Help? (Join the Game Dev Team!) 🤝

If you have awesome ideas, find a bug, or just want to help make this project more amazing, please let us know! You could be part of building the future of AI games!

*Remember to save and backup your work after any changes!* 💾
