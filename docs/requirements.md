# Requirements

## Stakeholder Needs

| ID | How our application will meet the need |
|---|---|
| SN0 | Test the main features and show clear error messages when an action fails. |
| SN1 | Allow users to create secure accounts and create or access projects. |
| SN2 | Show the capacity and availability of each hardware set. |
| SN3 | Allow users to request available equipment. |
| SN4 | Record equipment checkouts for a project and update availability. |
| SN5 | Record equipment returns and update availability. |
| SN6 | Use a sprint plan and design the application to support more equipment types later. |

## System Requirements

| ID | Requirement | Stakeholder needs met |
|---|---|---|
| SR1 | The app shall provide sign-in and a New User popup where users can enter a userid and password. | SN1 |
| SR2 | The app shall securely protect the userid and password. | SN1 |
| SR3 | The app shall allow a user to create a project with a name, description, and project ID. | SN1 |
| SR4 | The app shall allow a user to access an existing project. | SN1 |
| SR5 | The app shall display the total capacity and current availability of HWSet1 (camera kits) and HWSet2 (audio and lighting kits). | SN2 |
| SR6 | The app shall allow a user to request an available quantity of equipment. | SN3 |
| SR7 | The app shall record equipment checkouts for a project and update availability. | SN4 |
| SR8 | The app shall let users specify how many units of each hardware set to check in, record the return, and update availability. | SN5 |
| SR9 | The app shall store user, project, hardware, and checkout information in a database accessible through an API. | SN1, SN2, SN3, SN4, SN5 |
| SR10 | The team shall test the main features and track defects. | SN0 |
| SR11 | The team shall deliver the proof of concept through planned sprints and support adding more hardware sets later. | SN6 | 
