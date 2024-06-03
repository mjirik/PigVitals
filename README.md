# PigVitals

PigVitals is an application designed to monitor and record the vital signs of pigs after liver transaplantation. This application is useful for doctors in Biomedical Center Of Charles University in Pilsen.

![PigVitals Video Guide](/demo/demo_vid.gif)


## Features

- Historical data recordings using mongoDB
- Easy depolyment using Docker
- User-friendly application
- Interactive reporting using Plotly

## Installation
Since the REST API for video procesing is using big neural network models, it is highly recomended to use GPU.
To get started with PigVitals, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/kubarada/PigVitals.git
    ```
2. Navigate to the project directory:
    ```bash
    cd PigVitals
    ```
3. Install the required dependencies:
    ```bash
    docker-compose.yaml --build
    ```

## Application 
The application visualizes data from MongoDB provided by a REST API that processes video content. It analyzes videos, turning insights into clear visual representations. This helps users quickly understand and make decisions based on the video data. Web application was build using Flask, while the REST API uses mainly MMTracking for video procesing, with the usage of neural network models.
  ![PigVitals Video Guide](/demo/detail_1.png)
  ![PigVitals Video Guide](/demo/detail_2.png)
