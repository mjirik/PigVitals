ARG PYTORCH="1.6.0"
ARG CUDA="10.1"
ARG CUDNN="7"
ARG MM="2.8.0"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel

ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"

# To fix GPG key error when running apt-get update
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install mmcv-full -f https://download.openmmlab.com/mmcv/dist/cu101/torch1.6.0/index.html
RUN pip install mmdet==2.27

RUN conda clean --all
ENV FORCE_CUDA="1"

# Set the working directory to the MMTracking directory
WORKDIR /usr/src/app
COPY . .
# Install MMTracking requirements and package
RUN pip install -r mmtracking/requirements/build.txt
WORKDIR /usr/src/app/mmtracking
COPY . .
RUN pip install -e .

ARG DEBIAN_FRONTEND=noninteractive
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install pymongo
RUN pip install flask
RUN pip uninstall opencv-python -y
RUN conda install -c conda-forge opencv

WORKDIR /usr/src/app
COPY . .
EXPOSE 8080
# Run the application
CMD ["python", "processor.py"]