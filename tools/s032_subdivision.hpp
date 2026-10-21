// Independent subdivision suppression check; no Boyer-Myrvold calls.
// Every accepted negative layer clause forbids a K5 or K3,3 subdivision.
#include <queue>
#include <set>
#include <vector>
#include <utility>
static bool s032_subdivision(int n, const std::vector<std::pair<int,int>>& es) {
  std::vector<std::set<int>> a(n);
  for(auto e:es) {
    int u=e.first,v=e.second;
    if(u<0||v<0||u>=n||v>=n||u==v||a[u].count(v)) return false;
    a[u].insert(v); a[v].insert(u);
  }
  for(;;) {
    int v=-1;
    for(int i=0;i<n;i++) if(a[i].size()==2) {v=i;break;}
    if(v<0) break;
    auto it=a[v].begin();int x=*it++,y=*it;
    if(a[x].count(y)) return false;
    a[x].erase(v);a[y].erase(v);a[v].clear();
    a[x].insert(y);a[y].insert(x);
  }
  std::vector<int> vs;
  for(int i=0;i<n;i++) if(!a[i].empty()) vs.push_back(i);
  if(vs.size()==5) {
    for(int i:vs) if(a[i].size()!=4) return false;
    return true;
  }
  if(vs.size()!=6) return false;
  for(int i:vs) if(a[i].size()!=3) return false;
  std::vector<int> col(n,-1);std::queue<int> q;
  col[vs[0]]=0;q.push(vs[0]);int visited=0,ones=0;
  while(!q.empty()) {
    int v=q.front();q.pop();visited++;ones+=col[v];
    for(int w:a[v]) {
      if(col[w]<0) {col[w]=1-col[v];q.push(w);}
      else if(col[w]==col[v]) return false;
    }
  }
  return visited==6 && ones==3;
}
