/* Six original flight patterns inspired by early fixed-screen arcades.
   Positions stay within the DMG playfield. Logic remains at 25 ticks/s. */
#define FORMATION 0
#define DIVE 1
#define FEINT 2
#define RETURNING 3
#define WAIT_ENTRY 4
#define ENTERING 5
#define LAUNCH_WAIT 6
uint8_t home_x[10],home_y[10],hunt_target[10],flight_clock[10],flight_side[10];
uint8_t formation_drift,hunter_active,hunter_solo,launch_serial;
uint8_t pattern_id,composition_id,crow_budget,inv_offset,inv_drop,inv_retreat;
int8_t inv_direction;
uint16_t wave_rng;
const int8_t wave_sine[64]={0,1,2,3,4,4,5,6,6,7,8,8,9,9,9,9,9,9,9,9,9,8,8,7,6,6,5,4,4,3,2,1,0,-1,-2,-3,-4,-4,-5,-6,-6,-7,-8,-8,-9,-9,-9,-9,-9,-9,-9,-9,-9,-8,-8,-7,-6,-6,-5,-4,-4,-3,-2,-1};
uint8_t approach(uint8_t value,uint8_t target,uint8_t speed){
 if(value<target)return target-value>speed?value+speed:target;
 return value-target>speed?value-speed:target;
}
uint8_t flight_x(int16_t x){uint8_t right=wave<3?102:94;if(x<2)return 2;if(x>right)return right;return x;}
/* Maximal 16-bit Galois LFSR; seed once per new game, not per wave. */
void waves_seed(void){wave_rng=sys_time^0xace1;if(!wave_rng)wave_rng=1;}
uint8_t flight_random(void){wave_rng=(wave_rng>>1)^((wave_rng&1)?0xb400u:0);return (uint8_t)wave_rng;}
uint8_t wave_choice(uint8_t n){uint8_t r;do{r=flight_random();}while(r>=252);return r%n;}
void waves_setup(void){uint8_t i,n,large;formation_drift=0;hunter_active=0;hunter_solo=0;attack_pair=0;attack_cd=32;launch_serial=0;
 pattern_id=1+wave_choice(7);composition_id=wave<3||pattern_id==7?3:wave_choice(3);
 n=composition_id==3?10:6;large=composition_id==3?0:6-composition_id*2;
 crow_budget=4;inv_offset=0;inv_drop=0;inv_retreat=0;inv_direction=1;
 if(pattern_id==7){fire_period=phase<5?18-phase*2:8;fire_cd=fire_period;}
 for(i=0;i<10;i++){
  foes[i].live=i<n;foes[i].kind=i<large?(wave<5?1:2):0;
  home_x[i]=composition_id==3?6+(i%5)*18:14+(i%3)*30;home_y[i]=12+(i/(composition_id==3?5:3))*24;
  flight_clock[i]=i*3;flight_side[i]=i&1;hunt_target[i]=home_x[i];
  foes[i].x=(i&1)?102:2;foes[i].y=0;foes[i].mode=WAIT_ENTRY;
 }
}
/* No CROW alive or queued; reuse free slots after hiding the destroyed sprite. */
void waves_reinforce(uint8_t killed){uint8_t i,count,k=0;
 if(!foes[killed].kind||!crow_budget)return;
 for(i=0;i<10;i++)if(foes[i].live&&!foes[i].kind)return;
 count=1+wave_choice(crow_budget);
 for(i=0;i<10 && k<count;i++)if(!foes[i].live){
  hide_enemy(i);foes[i].kind=0;foes[i].live=1;foes[i].mode=WAIT_ENTRY;
  foes[i].x=k&1?102:2;foes[i].y=0;
  home_x[i]=8+k*24;home_y[i]=4+(k&1)*12;flight_clock[i]=12+k*5;flight_side[i]=k&1;hunt_target[i]=home_x[i];
  k++;crow_budget--;
 }
}
void invaders_move(void){uint8_t i,alive=0,speed;
 for(i=0;i<10;i++)if(foes[i].live)alive++;
 speed=2+(alive<=4);
 if(inv_drop>=66)inv_retreat=1;
 if(inv_retreat){if(inv_drop)inv_drop-=2;else inv_retreat=0;}
 if((inv_direction>0 && inv_offset+speed>20)||(inv_direction<0 && inv_offset<speed)){
  inv_direction=-inv_direction;if(!inv_retreat)inv_drop+=6;
 }else inv_offset+=inv_direction*speed;
 for(i=0;i<10;i++)if(foes[i].live){Enemy *e=&foes[i];
  if(e->mode==WAIT_ENTRY){if(flight_clock[i])flight_clock[i]--;else e->mode=ENTERING;continue;}
  e->x=approach(e->x,home_x[i]+inv_offset,4);e->y=approach(e->y,home_y[i]+inv_drop,3);
  if(e->mode==ENTERING && e->x==home_x[i]+inv_offset && e->y==home_y[i]+inv_drop)e->mode=FORMATION;
 }
}
void launch_flight(uint8_t i,int8_t offset){
 foes[i].mode=DIVE;flight_clock[i]=0;flight_side[i]=(launch_serial+i)&1;
 hunt_target[i]=flight_x((int16_t)px+4+offset);
}
void waves_move(void){uint8_t i,n=10,active=0,ready=0,alive=0,limit,group,start,launched=0;
 uint8_t difficulty=phase>5?4:phase-1,gap,home;int16_t target;
 if(pattern_id==7){invaders_move();return;}
 if((ticks&63)==0 && formation_drift<24)formation_drift++;
 for(i=0;i<n;i++)if(foes[i].live){Enemy *e=&foes[i];alive++;home=home_y[i]+formation_drift;
  if(e->mode==WAIT_ENTRY){if(flight_clock[i])flight_clock[i]--;else{e->mode=ENTERING;flight_clock[i]=0;}continue;}
  if(e->mode==ENTERING){
   flight_clock[i]++;target=home_x[i];
   if(flight_clock[i]<24)target+=wave_sine[(flight_clock[i]*2+(flight_side[i]?32:0))&63];
   e->x=approach(e->x,flight_x(target),3);e->y=approach(e->y,home,2);
   if(flight_clock[i]>=24 && e->x==home_x[i] && e->y==home){e->mode=FORMATION;flight_clock[i]=0;}
   continue;
  }
  if(e->mode==FORMATION){
   target=home_x[i]+wave_sine[((ticks>>1)+(pattern_id==4?i*9:0))&63];e->x=flight_x(target);e->y=home;
   if(pattern_id==4)e->y=home+10+wave_sine[((ticks>>1)+i*13)&63];
   ready++;continue;
  }
  active++;
  if(e->mode==RETURNING){
   target=e->y>home+18?(flight_side[i]?94:2):home_x[i];
   e->x=approach(e->x,flight_x(target),3);e->y=approach(e->y,home,3);
   if(e->y==home && e->x==home_x[i]){e->mode=FORMATION;flight_clock[i]=0;}
   continue;
  }
  if(e->mode==LAUNCH_WAIT){if(flight_clock[i])flight_clock[i]--;else e->mode=DIVE;continue;}
  if(e->mode==FEINT){
   if(++flight_clock[i]>=10){e->mode=DIVE;flight_clock[i]=19;hunt_target[i]=flight_x(px+4);fire_enemy(e->x+(e->kind?8:4),e->y+(e->kind?14:8));}
   continue;
  }
  flight_clock[i]++;
  if((pattern_id==3 && flight_clock[i]==18)||(pattern_id==4 && flight_clock[i]==12)){e->mode=FEINT;flight_clock[i]=0;continue;}
  if(pattern_id==6 && flight_clock[i]==10)hunt_target[i]=flight_x(px+4);
  target=hunt_target[i];
  if(pattern_id==1)target+=wave_sine[(flight_clock[i]*2+(flight_side[i]?32:0))&63];
  if(pattern_id==2||pattern_id==5)target+=wave_sine[(flight_clock[i]*3+(flight_side[i]?32:0))&63]*2;
  if(pattern_id==4)target+=wave_sine[(ticks*3+i*9)&63];
  if(pattern_id==6)target+=wave_sine[(flight_clock[i]*3+i*11)&63]*3;
  if(e->y<88||pattern_id==6)e->x=approach(e->x,flight_x(target),e->kind?3:2);
  e->y+=2+(!e->kind?(flight_clock[i]&1):(difficulty>=2 && (ticks&1)));
  if(flight_clock[i]==14 && e->y<88)fire_enemy(e->x+(e->kind?8:4),e->y+(e->kind?14:8));
  if(e->y>=130)e->mode=RETURNING;
 }
 hunter_active=active;
 if(attack_cd)attack_cd--;
 if(!ready||attack_cd)return;
 limit=pattern_id==1||pattern_id==3?2:(pattern_id==6?4:3);
 group=pattern_id==2||pattern_id==3?2:(pattern_id==5?3:1);
 gap=pattern_id==1?32:(pattern_id==2?34:(pattern_id==3?44:(pattern_id==4?24:(pattern_id==5?52:16))));
 gap-=difficulty*2;if(alive<=3)gap>>=1;if(gap<8)gap=8;
 if(active>=limit)return;
 start=flight_random();while(start>=n)start-=n;
 for(i=0;i<n && launched<group && active<limit;i++){
  uint8_t slot=start+i;if(slot>=n)slot-=n;
  if(foes[slot].live && foes[slot].mode==FORMATION){
   launch_flight(slot,group==1?0:(launched==0?-12:(launched==1?12:0)));if(launched){foes[slot].mode=LAUNCH_WAIT;flight_clock[slot]=launched*6;}launched++;active++;
  }
 }
 if(launched){launch_serial++;attack_cd=gap;}else attack_cd=8;
}
