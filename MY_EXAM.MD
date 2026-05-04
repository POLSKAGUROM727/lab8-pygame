## Feature: Screen Wrapping

- remove existing boundry constraint function
- basically teleport the square to the other side when it touches the border

## Feature: Eating and ++

- bigger squares will eat smaller squares when they are colliding
- use the collision function to detect if a bigger square can eat a smaller one
- eaten squares will just die and respawn with the same size
- after getting eaten the bigger square grows depending on the size of the smaller square
