// S045 interactive extension of attributed bipsat2/S032 guarded propagator.
// A colouring-partition clause is necessary for every non-k-colourable graph.
#include <iostream>
#include <sstream>
#include <set>

struct S045Terminator : CaDiCaL::Terminator {
  double deadline, last = 0;
  std::string stop;
  BipPropagator *prop;
  bool terminate () override {
    double t = now_s();
    if (t-last >= 5) {
      last=t;
      printf("c S045 checks=%ld cuts=%ld models=%ld\n",prop->n_checks,prop->n_lemmas_written,prop->n_model_checks);
      fflush(stdout);
      if(prop->lemma_out) {fflush(prop->lemma_out); _commit(_fileno(prop->lemma_out));}
    }
    return t >= deadline || (!stop.empty() && std::filesystem::exists(stop));
  }
};

int main(int argc, char **argv) {
  if(argc != 7) die("usage: instance lemmas seconds stop-file positive-phases mode");
  FILE *f=fopen(argv[1],"r");
  if(!f) die("cannot open instance");
  int n,m,extra,nc;
  if(fscanf(f,"p bipsat2 %d %d %d %d",&n,&m,&extra,&nc)!=4 || n<1 || m<0 || extra<0 || nc<0) die("bad header");
  std::vector<std::pair<int,int>> edges;
  std::set<std::pair<int,int>> unique;
  for(int i=0;i<m;i++) {
    int a,b;
    if(fscanf(f," e %d %d",&a,&b)!=2 || a<0 || a>=b || b>=n || !unique.insert({a,b}).second) die("bad pair map");
    edges.emplace_back(a,b);
  }
  CaDiCaL::Solver solver;
  solver.set("quiet",1);
  BipPropagator prop(n,m,edges);
  solver.connect_external_propagator(&prop);
  solver.resize(2*m+extra);
  for(int v=1;v<=2*m;v++) solver.add_observed_var(v);
  for(int c=0;c<nc;c++) {
    int lit;
    do {
      if(fscanf(f," %d",&lit)!=1 || abs(lit)>2*m+extra) die("bad clause");
      solver.add(lit);
    } while(lit);
  }
  fclose(f);
  auto loaded=load_validated_lemmas(argv[2],n,edges,&solver,nullptr);
  if(loaded.rejected_format || loaded.rejected_planar || loaded.incomplete) die("invalid geometric checkpoint");
  prop.n_lemmas_loaded=loaded.loaded;
  prop.lemma_out=fopen(argv[2],"a");
  if(!prop.lemma_out) die("cannot open lemma journal");
  if(atoi(argv[5])) for(int v=1;v<=2*m;v++) solver.phase(v);
  std::string mode=argv[6];
  if(mode!="partition" && mode!="block") die("bad feedback mode");
  S045Terminator term;
  term.deadline=now_s()+atof(argv[3]); term.stop=argv[4]; term.prop=&prop;
  solver.connect_terminator(&term);
  long models=0;
  for(;;) {
    int res=solver.solve();
    if(res!=10) {
      printf("END %d %ld %ld\n",res,models,prop.n_lemmas_written); fflush(stdout); return res;
    }
    if((int)prop.model_val.size()!=2*m+1) die("incomplete model");
    // Fresh native checks in addition to propagator model checks.
    PlanarityChecker fresh(n,m);
    std::vector<std::pair<int,int>> ls[2],kur;
    for(int i=0;i<m;i++) for(int k=0;k<2;k++) if(prop.model_val[2*i+1+k]>0) ls[k].push_back(edges[i]);
    if(!fresh.check(ls[0],kur) || !fresh.check(ls[1],kur)) die("nonplanar candidate");
    models++;
    printf("CAND %ld ",models);
    for(int v=1;v<=2*m;v++) putchar(prop.model_val[v]>0?'1':'0');
    putchar('\n'); fflush(stdout);
    std::string line;
    if(!std::getline(std::cin,line) || line=="STOP") {printf("STOPPED %ld\n",models);fflush(stdout);return 0;}
    std::istringstream in(line);
    std::string tag,junk; int k;
    if(!(in>>tag>>k) || tag!="COLOR" || k<1 || k>n) die("bad colour header");
    std::vector<int> col(n);
    for(int &c:col) if(!(in>>c) || c<0 || c>=k) die("bad colour vector");
    if(in>>junk) die("excess colour data");
    for(int i=0;i<m;i++) if((prop.model_val[2*i+1]>0 || prop.model_val[2*i+2]>0) && col[edges[i].first]==col[edges[i].second]) die("improper feedback colouring");
    if(mode=="partition") {
      for(int i=0;i<m;i++) if(col[edges[i].first]==col[edges[i].second]) {
        solver.add(2*i+1); solver.add(2*i+2);
      }
    } else {
      for(int v=1;v<=2*m;v++) solver.add(prop.model_val[v]>0?-v:v);
    }
    solver.add(0);
  }
}
