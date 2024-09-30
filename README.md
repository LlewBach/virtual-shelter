# Milestone 4 Project - Virtual Shelter
By Gareth Llewelyn

[View deployed Heroku site]()

![Am I Responsive]()

# Table of contents

> 1. [Overview](#overview)
> 2. [UX](#ux)
>> 1. [Strategy](#strategy)
>> 2. [Scope](#scope)
>> 3. [Structure](#structure)
>> 4. [Skeleton](#skeleton)
>> 5. [Surface](#surface)
> 3. [Features](#features)
>> 1. [Existing Features](#existing-features)
>> 2. [Future Feature Considerations](#future-feature-considerations)
> 4. [Technologies Used](#technologies-used)
> 5. [Testing](#testing)
> 6. [Deployment](#deployment)
> 7. [Credits](#credits)
> 8. [Acknowledgements](#acknowledgements)
> 9. [Disclaimer](#disclaimer)

# Overview

[Back to top](#milestone-4-project---virtual-shelter)

Virtual Shelter is an app where animal rescue shelters can upload profiles of their animals for users to virtually foster them and contribute to their care.

# UX

[Back to top](#milestone-4-project---virtual-shelter)

## Strategy

[Back to top](#milestone-4-project---virtual-shelter)

Creator's goals...

- to create an additional income stream for animal shelters

User's goals...

- to be able to support a shelter that's important to them
- to enjoy the challenge of fostering a virtual animal in an emotionally engaging way

### User Stories

| User Story ID                        | As A(n)              | I want to be able to                                   | so that I can                                     |
| ------------------------------------ | -------------------- | ------------------------------------------------------ | ------------------------------------------------- |
| **Viewing and Navigation**           |                      |                                                        |                                                   |
| 1a                                   | Visitor              | Understand the purpose of the site immediately         | Decide whether I want to engage with it.          |
| 1b                                   | User                 | Navigate and interact with the site on all viewports   | Engage with the site on any device.               |
| 1c                                   | User                 | View information about the site                        | Understand how to use it.                         |
| **User Authentication and Profiles** |                      |                                                        |                                                   |
| 2a                                   | Visitor              | Create an account                                      | Access the features of the web app.               |
| 2b                                   | User                 | Log in                                                 | Access my profile and interact with the app.      |
| 2c                                   | User                 | Log out                                                | Secure my account after use.                      |
| 2d                                   | User                 | Reset my password if I forget it                       | Regain access to my account.                      |
| 2e                                   | User                 | Update my profile details                              | Keep my information current.                      |
| 2f                                   | User                 | Delete my account                                      | Delete information related to me if I so wish.    |
| 2g                                   | Shelter staff member | Log in as a shelter admin                              | Manage the animals listed from my shelter.        |
| 2h                                   | Admin                | Manage user accounts and shelter profiles              | Maintain the integrity of the platform.           |
| 2i                                   | Admin                | Generate reports on virtual fostering activities       | Monitor platform usage and impact.                |
| **Animal Shelter Management**        |                      |                                                        |                                                   |
| 3a                                   | Shelter staff member | Create a new shelter profile                           | Add my shelter's details to the platform.         |
| 3b                                   | Shelter staff member | Add animal profiles to the shelter's profile           | Facilitate their virtual fostering.               |
| 3c                                   | Shelter staff member | Update animal profiles                                 | Keep information about them accurate and current. |
| 3d                                   | Shelter staff member | Delete animal profiles                                 | Remove animals that are adopted.                  |
| 3e                                   | Shelter staff member | Get information about fosterer engagement with shelter | Make informed decisions about engaging users.     |
| 3f                                   | Shelter staff member | Send updates about the animals to their fosterers      | Keep them connected and informed.                 |
| **Virtual Fostering**                |                      |                                                        |                                                   |
| 4a                                   | User                 | Browse animals available for virtual fostering         | Choose one to support.                            |
| 4b                                   | User                 | Virtually foster an animal                             | Support it through the platform.                  |
| 4c                                   | User                 | Interact with a virtual animal                         | Simulate taking care of it.                       |
| 4d                                   | User                 | Be notified when my pet needs attention                | Keep on top of its care.                          |
| 4e                                   | User                 | Receive rewards for maintaining healthy pets           | Be encouraged to continue fostering.              |
| 4f                                   | User                 | Receive updates on the real animal I am fostering      | Be informed about its well-being.                 |
| **Payments and Sponsorship**         |                      |                                                        |                                                   |
| 5a                                   | User                 | Choose a sponsorship plan / animal                     | Foster according to my financial capability.      |
| 5b                                   | User                 | Make secure payments                                   | Support the shelter.                              |
| 5c                                   | User                 | Receive confirmation of payments                       | Have a record of my support.                      |
| **Social and Community Features**    |                      |                                                        |                                                   |
| 6a                                   | User                 | See a leaderboard or community board of top fosterers  | Engage with the community.                        |

## Scope

[Back to top](#milestone-4-project---virtual-shelter)

### Functional Requirements

#### Simple and intuitive interface

- Users can navigate through the site easily
- Users get feedback and confirmation for their actions
- Users can use site on a range of device sizes

#### Profile management

- Users can register, login, logout and edit profile
- Users can request to be made a Shelter Admin
- Shelter Admins can manage a shelter's profile
- Shelter Admins can upload and manage animal profiles
- Shelter Admins can provide updates on animal profiles

#### Virtual fostering

- Users can browse animal profiles to choose which to virtually foster
- Users can customize their own virtual animal from a choice of breeds and colours

#### Dashboard

- Users can view fostered animals
- Users can take care of fostered animals
- Users can assess animal stats
- Dashboard should update 'live'

#### Tokens

- Users can purchase tokens securely via Stripe
- Users can spend tokens on their fostered animals

### Content Requirements

#### Media

- Users can upload pictures for profiles

#### Sprite Sheets

- A variety of sprite sheets for different animals

#### Game play

- Sprites will have multiple states to boost interactivity
- Users can interact with sprite via button(s)
- Sprite stats will be shown and updated live

## Structure

[Back to top](#milestone-4-project---virtual-shelter)

### UX Information Structure

Logged in users will have the following navbar links: Virtual Shelter(Home), Dashboard, Profile/My Shelter, Shelters, Animals, Log Out. This will enable users to care for their fostered animals, manage their personal information and browse shelters and animals in need of support.

### Application Information Flow

As the dashboard needs to update itself 'live' and when accessed after extended periods of disuse, this project requires the use of AJAX to connect the front end to the backend.

## Skeleton

[Back to top](#milestone-4-project---virtual-shelter)

### Wireframes

[Home page wireframe](static/wireframes/home-wireframe.png)

[Dashboard page wireframe](static/wireframes/dashboard-wireframe.png)

[Shelters page wireframe](static/wireframes/shelters-wireframe.png)

[Animals page wireframe](static/wireframes/animals-wireframe.png)

### Database

## Surface

[Back to top](#milestone-4-project---virtual-shelter)

# Features

[Back to top](#milestone-4-project---virtual-shelter)

## Existing Features

[Back to top](#milestone-4-project---virtual-shelter)

## Future Feature Considerations

[Back to top](#milestone-4-project---virtual-shelter)

# Technologies Used

[Back to top](#milestone-4-project---virtual-shelter)

# Testing

[Back to top](#milestone-4-project---virtual-shelter)

# Deployment

[Back to top](#milestone-4-project---virtual-shelter)

# Credits

[Back to top](#milestone-4-project---virtual-shelter)

- https://www.youtube.com/watch?v=zOtxP7ahi4M - How To Make Responsive Navbar with Bootstrap 5 | Step by Step Tutorial - Web Dev Creative

- Mentor Ben Kav - README structure

# Acknowledgements

[Back to top](#milestone-4-project---virtual-shelter)

# Disclaimer

[Back to top](#milestone-4-project---virtual-shelter)