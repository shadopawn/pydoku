## Other windows than main are not updating.

### Description
Row, column, or block windows are not updated when something has changed in the main window.

### What needs to happen?
Block window needs to show the exact value as the main window when some value entered to the corresponding cell in the main window.

### What happened instead?
Block window still empty after entering some value to the main window.

### How to replicate?

- Run the program
- Open the main window by clicking **Open Full Board** button
- Open the first block window by clicking **(1,1)** button among **Open Block Window** button group
- Click **Generate** button to start a new game
- See the block window is still empty even though main window displays the initial game
- Change something in main window (add a number to one of the empty cells in the first block) and it is not reflected in that block
