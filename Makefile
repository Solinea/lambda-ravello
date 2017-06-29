#
build:
	lambda-uploader --publish  ./audit \
	                --config ./audit/lambda.json


default: build

