# Virtual Shelter - Testing Documentation

The README can be found under [README.md](README.md)

# Table of contents

> 1. [User Story Testing](#user-story-testing)
> 2. [Unit Testing](#unit-testing)
> 3. [Responsiveness Testing](#responsiveness-testing)
> 4. [Browser Testing](#browser-testing)
> 5. [Code Validation](#code-validation)
> 6. [Significant Bugs](#significant-bugs)

# User Story Testing

[Back to top](#virtual-shelter---testing-documentation)

xxx

# Unit Testing

[Back to top](#virtual-shelter---testing-documentation)

xxx

# Responsiveness Testing

[Back to top](#virtual-shelter---testing-documentation)

xxx

# Browser Testing

[Back to top](#virtual-shelter---testing-documentation)

xxx

# Code Validation

[Back to top](#virtual-shelter---testing-documentation)

xxx

# Significant Bugs

[Back to top](#virtual-shelter---testing-documentation)

## Inconsistent spritesheet frame dimensions

Fixed: Yes

The spritesheet frame dimensions vary not only between dogs and colours, but also states within the same dog and colour! The consequence of this if left unresolved would be glitchy sprite animations. After contacting the creator to ask if the frames could be made a consistent size, she told me that this was her first time making spritesheets and that the answer was basically no. After consideration, I realised I could solve this by setting sprite.width by conditional statements based on the url passed into the Game class instantiation. See dashboard/static/dashboard/js/states/states.js.