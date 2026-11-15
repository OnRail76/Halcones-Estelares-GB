/* Four attacks drawn from a shuffled bag, announced before firing. */
uint8_t boss_bag[4],boss_pick,boss_attack,boss_rng,boss_left,boss_gap,boss_target;
uint8_t boss_random(void){boss_rng^=boss_rng<<3;boss_rng^=boss_rng>>5;boss_rng^=boss_rng<<1;return boss_rng;}
void boss_init(void){uint8_t i;
 boss_max_hp=32+(phase<11?phase-1:10)*8;boss_hp=boss_max_hp;boss_crack3=boss_max_hp>>2;boss_crack2=boss_max_hp>>1;boss_crack1=boss_max_hp-boss_crack3;
 boss_rng=(uint8_t)sys_time^(uint8_t)score^(phase*31)^px;if(!boss_rng)boss_rng=93;
 boss_pick=4;boss_attack=255;boss_left=0;boss_gap=0;fire_cd=40;
 for(i=0;i<10;i++){foes[i].live=0;hide_enemy(i);}
}
void boss_shot(uint8_t x,int8_t dx){uint8_t i;for(i=0;i<3;i++)if(!plasma[i].live){
 plasma_aim[i]=boss_attack==1;plasma_error[i]=0;plasma_span[i]=boss_target>x?boss_target-x:x-boss_target;plasma[i].x=x;plasma[i].y=MOAI_Y+33;plasma[i].live=1;plasma_dx[i]=dx;sfx_start(FX_BOSS_FIRE);return;
}}
void boss_choose(void){uint8_t i,j,t;
 if(boss_pick==4){for(i=0;i<4;i++)boss_bag[i]=i;
  for(i=3;i;i--){j=boss_random()%(i+1);t=boss_bag[i];boss_bag[i]=boss_bag[j];boss_bag[j]=t;}boss_pick=0;
 }
 boss_attack=boss_bag[boss_pick++];boss_target=px+8;boss_left=boss_attack==0?3:(boss_attack==1?2:1);boss_gap=12;
 moai_expression(1,0,0);
}
void boss_tick(void){uint8_t i,x;int8_t dx;
 if(moai_intro)return;
 if(moai_mouth_timer)moai_mouth_timer--;
 if(boss_left){
  if(boss_gap)boss_gap--;else{
   moai_eye_side^=1;x=MOAI_X+(moai_eye_side?29:10);
   if(boss_attack==0)boss_shot(x,0); /* Alternating-eye burst. */
   if(boss_attack==1){dx=boss_target<x?-1:(boss_target>x?1:0);boss_shot(x,dx);}
   if(boss_attack==2){boss_shot(50,-1);boss_shot(60,0);boss_shot(70,1);}
   if(boss_attack==3)for(i=0;i<2;i++)if(!foes[i].live){
    foes[i].live=1;foes[i].x=i?96:8;foes[i].y=32;foes[i].mode=1;foes[i].kind=0;
    hunt_target[i]=boss_target;flight_clock[i]=0;
   }
   boss_left--;boss_gap=6;moai_mouth_timer=6;
   if(!boss_left){fire_cd=fire_period+18;boss_attack=255;}
  }
 }else if(!fire_cd)boss_choose();
 moai_expression(boss_left || moai_mouth_timer,moai_mouth_timer!=0,0);
 for(i=0;i<2;i++)if(foes[i].live){Enemy *e=&foes[i];
  if(e->mode==1){e->y+=2;if(e->y<94)e->x=approach(e->x,hunt_target[i]>100?100:hunt_target[i],1);
   if(++flight_clock[i]==16)fire_enemy(e->x+4,e->y+8);
   if(e->y>=130)e->mode=3;
  }else{e->y=approach(e->y,24,3);e->x=approach(e->x,i?96:8,2);if(e->y==24){e->mode=1;flight_clock[i]=0;hunt_target[i]=px+8;}}
  if(hit(px+8,128,e->x-5,e->y-6,18,22)){
   if(shield_state==1){e->live=0;hide_enemy(i);boom(e->x,e->y);add_score(10);}else damage();
  }
 }
}
