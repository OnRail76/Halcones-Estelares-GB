/* Exact 1.3.3 damage thresholds and block-dissolve semantics; DMG tile geometry. */
#define MOAI_X 40
#define MOAI_Y 8
#define MOAI_W 40
#define MOAI_H 72
uint8_t moai_pixels[720],moai_stage,moai_eyes,moai_mouth,moai_eye_side;
uint8_t moai_flash,moai_blocks,moai_bidx,moai_mouth_timer;
uint8_t moon_x,moon_clock;
uint8_t moai_dirty[9],moai_cursor,moai_intro;
void moai_flush(void){uint8_t i,r;
 if(moai_intro){
  if(sys_time&1)return;r=9-moai_intro;
  set_bkg_data(64+r*5,5,moai_pixels+(uint16_t)r*80);moai_dirty[r]=0;
  for(i=0;i<5;i++){tmp[i]=64+r*5+i;field[(uint16_t)(1+r)*32+5+i]=tmp[i];}
  set_bkg_tiles(5,1+r,5,1,tmp);moai_intro--;return;
 }
 for(i=0;i<9;i++){r=moai_cursor;if(++moai_cursor==9)moai_cursor=0;if(moai_dirty[r]){set_bkg_data(64+r*5,5,moai_pixels+(uint16_t)r*80);moai_dirty[r]=0;return;}}
}

void moai_expression(uint8_t eyes,uint8_t mouth,uint8_t full){uint8_t y,i,hi,lo,inner_hi,inner_lo;uint16_t o;
 if(!full && eyes==moai_eyes && mouth==moai_mouth)return;
 memcpy(moai_pixels,moai_stages+(uint16_t)moai_stage*720,720);
 if(eyes)for(i=0;i<2;i++)for(y=14;y<20;y++){
  o=(uint16_t)(y>>3)*80+(i?48:0)+((y&7)<<1);
  hi=i?0x3f:0x01;lo=i?0x80:0xfc;
  inner_hi=(y>=16&&y<=18)?(i?0x1f:0):0;
  inner_lo=(y>=16&&y<=18)?(i?0:0xf8):0;
  moai_pixels[o]|=hi;moai_pixels[o+16]|=lo;
  moai_pixels[o+1]=(moai_pixels[o+1]&~hi)|inner_hi;
  moai_pixels[o+17]=(moai_pixels[o+17]&~lo)|inner_lo;
 }
 if(mouth)for(y=47;y<50;y++){
  o=(uint16_t)(y>>3)*80+16+((y&7)<<1);
  moai_pixels[o]&=0xf8;moai_pixels[o+1]&=0xf8;
  moai_pixels[o+16]=0;moai_pixels[o+17]=0;
  moai_pixels[o+32]&=0x1f;moai_pixels[o+33]&=0x1f;
 }
 if(full){for(i=0;i<9;i++)moai_dirty[i]=1;}
 else{
  if(eyes!=moai_eyes){moai_dirty[1]=1;moai_dirty[2]=1;}
  if(mouth!=moai_mouth){moai_dirty[5]=1;moai_dirty[6]=1;}
 }
 moai_eyes=eyes;moai_mouth=mouth;
}
void moai_setup(void){uint8_t i,j;
 moai_stage=0;moai_eyes=0;moai_mouth=0;moai_eye_side=0;moai_mouth_timer=0;moai_flash=0;moai_blocks=0;moai_bidx=0;moon_x=10;moon_clock=0;
 moai_cursor=0;moai_intro=9;moai_expression(0,0,1);packed_tiles(jupiter_data_rle,112,16,0);
 for(i=0;i<4;i++){for(j=0;j<4;j++){tmp[j]=112+i*4+j;field[(10+i)*32+10+j]=tmp[j];}set_bkg_tiles(10,10+i,4,1,tmp);}
}
void moai_damage(void){uint8_t stage=0;
 if(boss_hp<=boss_crack1)stage=1;
 if(boss_hp<=boss_crack2)stage=2;
 if(boss_hp<=boss_crack3)stage=3;
 if(stage!=moai_stage){moai_stage=stage;moai_expression(moai_eyes,moai_mouth,1);}}
void moai_death_begin(void){uint8_t i;for(i=0;i<10;i++){foes[i].live=0;hide_enemy(i);}moai_expression(0,0,1);moai_flash=8;moai_blocks=45;moai_bidx=0;hide_sprite(35);}
uint8_t moai_death_tick(void){uint8_t i,idx,tile=0;uint16_t j;

 if(moai_flash){
  moai_flash--;memcpy(moai_pixels,moai_stages+(uint16_t)moai_stage*720,720);
  if(moai_flash&1)for(j=0;j<720;j+=2)moai_pixels[j]|=moai_pixels[j+1];
  set_bkg_data(64,45,moai_pixels);return 0;
 }
 for(i=0;i<3 && moai_blocks;i++){
  idx=moai_bidx;set_bkg_tiles(5+idx%5,1+idx/5,1,1,&tile);field[(1+idx/5)*32+5+idx%5]=0;
  moai_bidx+=17;if(moai_bidx>=45)moai_bidx-=45;moai_blocks--;
 }
 if((moai_blocks&3)==0)noise();return moai_blocks==0;
}
