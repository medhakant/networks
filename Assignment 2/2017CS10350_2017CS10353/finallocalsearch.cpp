#include <bits/stdc++.h>
using namespace std;
#define pb push_back

int vocabularyCardinality, totalStrings, conversionCost, totalCost, maxLength, miniCost;
map<char, int> hashCode;
float maxTime;
char eof;
vector<char> letters;
vector<string> listOfStrings;
vector<vector<int> > matchingCost;
int threshold = 2, extraDash = 4;
vector<string> answerString;

vector<vector<int> > finalFreq;
vector<int> colCost;
int updAlphaCost, updDashCost;
fstream  output;
bool trimmed = false;

void writeToFile(){
	for(int i=0; i<answerString.size();i++){
		output << answerString[i] << "\n";
	}
}

//function assumes that all the strings in the vector are of same length
vector<string> trimstring(vector<string> gene){
	int left = INT_MAX, right = INT_MAX;
	vector<string> trim_gene;
	for(int i=0; i<gene.size();i++){
		string s = gene[i];
		int num_dashes,j;
		num_dashes = 0;
		j = 0;
		//find minimum number of left trailing dashes
		while(s[j]=='-' && j < s.length()){
			num_dashes++;
			j++;
		}
		left = (num_dashes<left)?num_dashes:left;
		num_dashes = 0;
		j = s.length()-1;
		//find minimum number of right trailing dashes
		while(s[j]=='-' && j >=0){
			num_dashes++;
			j--;
		}
		right = (num_dashes<right)?num_dashes:right;
	}

	if(right>0 || left>0)
		trimmed=true;
	//return the trimmed substring
	int len = gene[0].length() - left - right;
	for(int i=0; i<gene.size();i++){
		string s = gene[i];
		trim_gene.push_back(s.substr(left,len));
	}

	return trim_gene;
}

int calCost(int sIndex, int dashIndex, int alphaIndex, int hashCodeDash, int hashCodeAlpha)
{
	int tempCost = miniCost;
	tempCost = tempCost - colCost[dashIndex] - colCost[alphaIndex];
	// cout<<miniCost<<" "<<colCost[dashIndex]<<" "<<colCost[alphaIndex]<<endl;
	
	finalFreq[dashIndex][hashCodeAlpha]++;
	finalFreq[dashIndex][hashCodeDash]--;
	finalFreq[alphaIndex][hashCodeAlpha]--;
	finalFreq[alphaIndex][hashCodeDash]++;
	updDashCost = updAlphaCost = 0;

	for(int it=0;it<=vocabularyCardinality;it++)
	{
		for(int jt=it+1;jt<=vocabularyCardinality;jt++)
		{
			tempCost += (finalFreq[dashIndex][it]*finalFreq[dashIndex][jt]*matchingCost[it][jt]);
			updDashCost += (finalFreq[dashIndex][it]*finalFreq[dashIndex][jt]*matchingCost[it][jt]);
			tempCost += (finalFreq[alphaIndex][it]*finalFreq[alphaIndex][jt]*matchingCost[it][jt]);
			updAlphaCost += (finalFreq[alphaIndex][it]*finalFreq[alphaIndex][jt]*matchingCost[it][jt]);
		}
	}
	// cout<<updAlphaCost<<" "<<updDashCost<<endl;
	finalFreq[dashIndex][hashCodeAlpha]--;
	finalFreq[dashIndex][hashCodeDash]++;
	finalFreq[alphaIndex][hashCodeAlpha]++;
	finalFreq[alphaIndex][hashCodeDash]--;

	return tempCost;
}

void localSearchForward()
{
	vector<string> tempAnswerString = answerString;
	int newMaxLength = maxLength;
	if(!trimmed)
	{
		for(int i=0;i<totalStrings;i++)
			tempAnswerString[i] += "-";
		newMaxLength = maxLength+1;
		colCost.pb(0);
	}
	for(int i=0;i<totalStrings;i++)
	{
		for(int j=newMaxLength-1;j>=0;j--)
		{
			if(tempAnswerString[i][j]!='-' || j==0) continue;

			int k=j-1;
			while(k>0 && tempAnswerString[i][k]=='-')
				k--;
			if(tempAnswerString[i][k]=='-') continue;

			int hashCodeAlpha =  hashCode[tempAnswerString[i][k]];
			// cout<<"0\n";
			int cost = calCost(i, j, k, vocabularyCardinality, hashCodeAlpha);
			
			if(cost < miniCost)
			{
				tempAnswerString[i][j] = tempAnswerString[i][k];
				tempAnswerString[i][k] = '-';
				miniCost = cost;
				finalFreq[j][hashCodeAlpha]++;
				finalFreq[j][vocabularyCardinality]--;
				finalFreq[k][hashCodeAlpha]--;
				finalFreq[k][vocabularyCardinality]++;
				colCost[j] = updDashCost;
				colCost[k] = updAlphaCost;	
			}
		}
	}
	tempAnswerString = trimstring(tempAnswerString);
	answerString = tempAnswerString;
}

void localSearchBackward()
{
	vector<string> tempAnswerString = answerString;
	
	for(int i=0;i<totalStrings;i++)
	{
		for(int j=0;j<maxLength;j++)
		{
			if(tempAnswerString[i][j]!='-' || j==maxLength-1) continue;

			int k=j+1;
			while(k<maxLength-1 && tempAnswerString[i][k]=='-')
				k++;
			if(tempAnswerString[i][k]=='-') continue;

			int hashCodeAlpha =  hashCode[tempAnswerString[i][k]];
			// cout<<"1\n";
			int cost = calCost(i, j, k, vocabularyCardinality, hashCodeAlpha);
			
			if(cost < miniCost)
			{
				tempAnswerString[i][j] = tempAnswerString[i][k];
				tempAnswerString[i][k] = '-';
				miniCost = cost;
				finalFreq[j][hashCodeAlpha]++;
				finalFreq[j][vocabularyCardinality]--;
				finalFreq[k][hashCodeAlpha]--;
				finalFreq[k][vocabularyCardinality]++;
				colCost[j] = updDashCost;
				colCost[k] = updAlphaCost;		
			}
		}
	}
	
	answerString = tempAnswerString;
}

int bruteForceSearch(vector<int> & index, int level)
{
	int frequency[vocabularyCardinality+1];

	memset(frequency, 0, sizeof(frequency));

	int endOfString = 0;

	for(int i=0;i<totalStrings;i++)
	{
		if(index[i] >= listOfStrings[i].size()) 
		{
			endOfString++;
			continue;
		}

		int temp_char = hashCode[listOfStrings[i][index[i]]];
		frequency[temp_char] ++;
	}

	if(endOfString==totalStrings)
		return 0;

	int dashes = 0;
	for(int i=0;i<totalStrings;i++)
	{
		if(index[i] >= listOfStrings[i].size()) 
		{
			answerString[i]+="-";
			finalFreq[level][vocabularyCardinality]++;
			index[i]++;
			dashes++;
			continue;
		}

		int temp_char = hashCode[listOfStrings[i][index[i]]];

		if(level+listOfStrings[i].size()-index[i] == maxLength) 
		{
			finalFreq[level][temp_char]++;
			answerString[i]+=(listOfStrings[i][index[i]]);
			index[i]++;
			continue;
		}

		if(frequency[temp_char] < threshold) 
		{
			finalFreq[level][vocabularyCardinality]++;
			answerString[i]+="-";
			dashes++;
			continue;
		}

		finalFreq[level][temp_char]++;
		answerString[i]+=(listOfStrings[i][index[i]]);
		index[i]++;
	}

	int cost = 0;

	for(int i=0;i<=vocabularyCardinality;i++)
	{
		for(int j=i+1;j<=vocabularyCardinality;j++)
		{
			cost += (finalFreq[level][i]*finalFreq[level][j]*matchingCost[i][j]);
		}
	}

	colCost.pb(cost);

	return (dashes*conversionCost + cost + bruteForceSearch(index, level+1));
}

int main(int argc, char** argv)
{
	clock_t start, end; 
	start = clock();
	string line;
	vector<int> init_index;
    if(argc==3){
        ifstream input(argv[1]);
        getline(input,line);
        istringstream ss(line);
        ss >> maxTime;
        ss.str("");
        ss.clear();
        getline(input,line);
        ss.str(line);
        ss >> vocabularyCardinality;
        ss.str("");
        ss.clear();
        getline(input,line);
        ss.str(line);
        for(int i=0;i<vocabularyCardinality;i++){
            char vocab;
            ss >> vocab;
            letters.pb(vocab);
			hashCode[vocab] = i;
            ss >> vocab;
        }
        ss.str("");
        ss.clear();
        getline(input,line);
        ss.str(line);
        ss >> totalStrings;
        ss.str("");
        ss.clear();
        for(int i=0;i<totalStrings;i++){
            getline(input,line);
            ss.str(line);
            string gene;
            ss >> gene;
            init_index.pb(0);
            listOfStrings.pb(gene);
			int len = gene.length();
			maxLength = max(maxLength, len);
			answerString.pb("");
            ss.str("");
            ss.clear();
        }
        ss.str("");
        ss.clear();
        getline(input,line);
        ss.str(line);
        ss >> conversionCost;
        for(int i=0;i<vocabularyCardinality+1;i++){
            getline(input,line);
            ss.str("");
            ss.clear();
            ss.str(line);
            int mc;
            vector<int> temp;
            for(int j=0;j<vocabularyCardinality+1;j++){
                ss >> mc;
                temp.push_back(mc);
            }
            matchingCost.push_back(temp);             
        }

        for(int i=0; i<maxLength+extraDash;i++)
        {
        	vector<int> temp;
        	for(int j=0;j<=vocabularyCardinality;j++)
        	{
        		temp.pb(0);
        	}
        	finalFreq.pb(temp);
        }

        output.open(argv[2], ios::out);
    }

	miniCost = bruteForceSearch(init_index, 0);
	end = clock();
	double time_taken = double(end - start) / double(CLOCKS_PER_SEC);
	int i = 0;
	while(time_taken < (maxTime*60)-10 && i < 10000){
		localSearchForward();
		localSearchBackward();
		end = clock();
		time_taken = double(end - start) / double(CLOCKS_PER_SEC);
		i++;
	}
	
	writeToFile();
	output.close();
	for(int i=0;i<totalStrings;i++)
		cout<<answerString[i]<<endl;
	cout<<miniCost<<endl;
}