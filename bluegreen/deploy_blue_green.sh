#!/bin/bash
IS_GREEN=$(docker ps | grep green) # 현재 실행중인 App이 blue인지 확인합니다.

copy_uploaded_images() {
  local source_container=$1
  local target_container=$2

  echo "Copying uploaded images from $source_container to $target_container..."

  # 호스트로 파일 복사
  docker cp $source_container:/mos-server/static/uploaded_images ./uploaded_images

  # 대상 컨테이너로 파일 복사
  docker cp ./uploaded_images/. $target_container:/mos-server/static/uploaded_images

  # 호스트의 임시 파일 삭제
  rm -rf ./uploaded_images
}

if [ -z "$IS_GREEN" ]; then # blue라면

  echo "### BLUE => GREEN ###"

  echo "1. get green image"
  docker-compose pull green # green으로 이미지를 내려받습니다.

  echo "2. green container up"
  docker-compose up -d green # green 컨테이너 실행

  GREEN_CONTAINER_ID=$(docker ps -q -f name=green)

  while true; do
    echo "3. green health check..."
    sleep 3

    REQUEST=$(curl -s -o /dev/null -w "%{http_code}" https://www.mos-server.store) # green으로 request
    if [ "$REQUEST" -eq 200 ]; then # 서비스 가능하면 health check 중지
        echo "health check success"
        break
    fi
  done

  if [ "$(docker ps -q -f name=blue)" ]; then
    BLUE_CONTAINER_ID=$(docker ps -q -f name=blue)

    echo "4. Copy uploaded images from blue to green"
    copy_uploaded_images $BLUE_CONTAINER_ID $GREEN_CONTAINER_ID
  fi

  echo "5. reload nginx"
  sudo cp -p /etc/nginx/nginx-green.conf /etc/nginx/nginx.conf || exit 1
  sudo cp -p /etc/nginx/sites-available/fastapi-green /etc/nginx/sites-available/fastapi || exit 1
  sudo systemctl restart nginx || exit 1

  if [ "$(docker ps -q -f name=blue)" ]; then
    echo "6. blue container down"
    docker-compose stop blue
  fi

else
  echo "### GREEN => BLUE ###"

  echo "1. get blue image"
  docker-compose pull blue

  echo "2. blue container up"
  docker-compose up -d blue

  BLUE_CONTAINER_ID=$(docker ps -q -f name=blue)

  while true; do
    echo "3. blue health check..."
    sleep 3

    REQUEST=$(curl -s -o /dev/null -w "%{http_code}" https://www.mos-server.store) # blue로 request
    if [ "$REQUEST" -eq 200 ]; then # 서비스 가능하면 health check 중지
        echo "health check success"
        break
    fi
  done

  if [ "$(docker ps -q -f name=green)" ]; then
    GREEN_CONTAINER_ID=$(docker ps -q -f name=green)

    echo "4. Copy uploaded images from green to blue"
    copy_uploaded_images $GREEN_CONTAINER_ID $BLUE_CONTAINER_ID
  fi

  echo "5. reload nginx"
  sudo cp -p /etc/nginx/nginx-blue.conf /etc/nginx/nginx.conf || exit 1
  sudo cp -p /etc/nginx/sites-available/fastapi-blue /etc/nginx/sites-available/fastapi || exit 1
  sudo systemctl restart nginx || exit 1

  if [ "$(docker ps -q -f name=green)" ]; then
    echo "6. green container down"
    docker-compose stop green
  fi

fi
