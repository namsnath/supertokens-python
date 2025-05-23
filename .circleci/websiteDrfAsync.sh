python_version=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if [[ $(echo "$python_version >= 3.13" | bc -l) -eq 1 ]]; then
    pip install setuptools legacy-cgi
fi

coreDriverJson=`cat ../coreDriverInterfaceSupported.json`
coreDriverLength=`echo $coreDriverJson | jq ".versions | length"`
coreDriverArray=`echo $coreDriverJson | jq ".versions"`
echo "got core driver relations"

# get driver version
version=`cat ../setup.py | grep -e 'version='`
while IFS='"' read -ra ADDR; do
    counter=0
    for i in "${ADDR[@]}"; do
        if [ $counter == 1 ]
        then
            version=$i
        fi
        counter=$(($counter+1))
    done
done <<< "$version"

someFrontendTestsRan=false
i=0
coreDriverVersion=`echo $coreDriverArray | jq ". | last"`
coreDriverVersion=`echo $coreDriverVersion | tr -d '"'`
coreFree=`curl -s -X GET \
"https://api.supertokens.io/0/core-driver-interface/dependency/core/latest?password=$SUPERTOKENS_API_KEY&planType=FREE&mode=DEV&version=$coreDriverVersion&driverName=python" \
-H 'api-version: 1'`
if [[ `echo $coreFree | jq .core` == "null" ]]
then
    echo "fetching latest X.Y version for core given core-driver-interface X.Y version: $coreDriverVersion, planType: FREE gave response: $coreFree. Please make sure all relevant cores have been pushed."
    exit 1
fi
coreFree=$(echo $coreFree | jq .core | tr -d '"')

frontendDriverVersion=$1
frontendDriverVersion=`echo $frontendDriverVersion | tr -d '"'`

frontendVersionXY=`curl -s -X GET \
"https://api.supertokens.io/0/frontend-driver-interface/dependency/frontend/latest?password=$SUPERTOKENS_API_KEY&frontendName=website&mode=DEV&version=$frontendDriverVersion&driverName=node" \
-H 'api-version: 1'`
if [[ `echo $frontendVersionXY | jq .frontend` == "null" ]]
then
    echo "fetching latest X.Y version for frontend given frontend-driver-interface X.Y version: $frontendDriverVersion, name: website gave response: $frontend. Please make sure all relevant versions have been pushed."
    exit 1
fi
frontendVersionXY=$(echo $frontendVersionXY | jq .frontend | tr -d '"')

frontendInfo=`curl -s -X GET \
"https://api.supertokens.io/0/frontend/latest?password=$SUPERTOKENS_API_KEY&mode=DEV&version=$frontendVersionXY&name=website" \
-H 'api-version: 0'`
if [[ `echo $frontendInfo | jq .tag` == "null" ]]
then
    echo "fetching latest X.Y.Z version for frontend, X.Y version: $frontendVersionXY gave response: $frontendInfo"
    exit 1
fi
frontendTag=$(echo $frontendInfo | jq .tag | tr -d '"')
frontendVersion=$(echo $frontendInfo | jq .version | tr -d '"')

nodeVersionXY=`curl -s -X GET \
"https://api.supertokens.io/0/frontend-driver-interface/dependency/driver/latest?password=$SUPERTOKENS_API_KEY&mode=DEV&version=$frontendDriverVersion&driverName=node&frontendName=website" \
-H 'api-version: 1'`
if [[ `echo $nodeVersionXY | jq .driver` == "null" ]]
then
    echo "fetching latest X.Y version for driver given frontend-driver-interface X.Y version: $frontendDriverVersion gave response: $nodeVersionXY. Please make sure all relevant drivers have been pushed."
    exit 1
fi
nodeVersionXY=$(echo $nodeVersionXY | jq .driver | tr -d '"')

nodeInfo=`curl -s -X GET \
"https://api.supertokens.io/0/driver/latest?password=$SUPERTOKENS_API_KEY&mode=DEV&version=$nodeVersionXY&name=node" \
-H 'api-version: 0'`
if [[ `echo $nodeInfo | jq .tag` == "null" ]]
then
    echo "fetching latest X.Y.Z version for driver, X.Y version: $nodeVersionXY gave response: $nodeInfo"
    exit 1
fi
nodeTag=$(echo $nodeInfo | jq .tag | tr -d '"')

tries=1
while [ $tries -le 3 ]
do
    tries=$(( $tries + 1 ))
    ./setupAndTestWithFrontendWithDrfAsync.sh $coreFree $frontendTag $nodeTag
    if [[ $? -ne 0 ]]
    then
        if [[ $tries -le 3 ]]
        then
            rm -rf ../../supertokens-root
            rm -rf ../../supertokens-website
            echo "failed test.. retrying!"
        else
            echo "test failed for website tests... exiting!"
            exit 1
        fi
    else
        rm -rf ../../supertokens-root
        rm -rf ../../supertokens-website
        break
    fi
done
