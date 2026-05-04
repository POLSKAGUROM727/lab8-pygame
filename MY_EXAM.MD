## Feature: Screen Wrapping

- remove existing boundry constraint function
- basically teleport the square to the other side when it touches the border

## Feature: Eating and ++

- bigger squares will eat smaller squares when they are colliding
- use the collision function to detect if a bigger square can eat a smaller one
- bigger squares will eat smaller squares when they are colliding
- use the collision function to detect if a bigger square can eat a smaller one
- eaten squares will just die and respawn with the same size
- after getting eaten the bigger square grows depending on the size of the smaller square

## Feature: Trails

- the trail is drawn as connected lines before drawing the square each frame

## Visual Artifact

What is happening: the trail stays at the old position when wrapping

Fix: check whether the horizontal or vertical distance between two consecutive trail points exceeds half the screen width or height
