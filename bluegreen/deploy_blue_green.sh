#!/bin/bash
IS_GREEN=$(docker ps | grep green) # 현재 실행중인 App이 blue인지 확인합니다.

log_error() {
  echo "Error encountered: $1"
  echo "Error log:"
  cat "$2"
  exit 1
}

if [ -z "$IS_GREEN" ]; then # blue라면

  echo "### BLUE => GREEN ###"

  echo "1. get green image"
  docker-compose pull green 2> green_pull_error.log || log_error "Failed to pull green image" green_pull_error.log

  echo "2. green container up"
  docker-compose up -d green 2> green_up_error.log || log_error "Failed to start green container" green_up_error.log

  while [ 1 = 1 ]; do
    echo "3. green health check..."
    sleep 3

    REQUEST=$(curl -s -o /dev/null -w "%{http_code}" https://www.mos-server.store) # green으로 request
    if [ "$REQUEST" = "200" ]; then # 서비스 가능하면 health check 중지
      echo "health check success"
      break ;
    fi
  done;

  echo "4. reload nginx"
  sudo cp -p /etc/nginx/nginx-green.conf /etc/nginx/nginx.conf || exit 1
  sudo systemctl restart nginx || exit 1

  if [ "$(docker ps -q -f name=blue)" ]; then
    echo "5. blue container down"
    docker-compose stop blue
  fi

else
  echo "### GREEN => BLUE ###"

  echo "1. get blue image"
  docker-compose pull blue 2> blue_pull_error.log || log_error "Failed to pull blue image" blue_pull_error.log

  echo "2. blue container up"
  docker-compose up -d blue 2> blue_up_error.log || log_error "Failed to start blue container" blue_up_error.log

  while [ 1 = 1 ]; do
    echo "3. blue health check..."
    sleep 3

    REQUEST=$(curl -s -o /dev/null -w "%{http_code}" https://www.mos-server.store) # green으로 request
    if [ "$REQUEST" = "200" ]; then # 서비스 가능하면 health check 중지
      echo "health check success"
      break ;
    fi
  done;

  echo "4. reload nginx"
  sudo cp -p /etc/nginx/nginx-blue.conf /etc/nginx/nginx.conf || exit 1
  sudo systemctl restart nginx || exit 1

  if [ "$(docker ps -q -f name=green)" ]; then
    echo "5. green container down"
    docker-compose stop green
  fi

fi
