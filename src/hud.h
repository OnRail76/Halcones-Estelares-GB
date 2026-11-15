/* ZX 1.3.3 sidebar adapted to 48x144. Only changed tile rows enter VRAM. */
uint8_t hud_pixels[1728], hud_dirty[18], hud_valid,hud_cursor;
uint32_t hud_score, hud_record;
uint8_t hud_lives,hud_phase,hud_wave,hud_shield,hud_meter;
/* Packed row writes replace per-pixel multiplication and bit operations. */
void hud_bits(uint8_t x,uint8_t y,uint8_t width,uint16_t bits){
 uint16_t off=((uint16_t)(y>>3)*6+(x>>3))*16+((y&7)<<1);
 uint8_t shift=16-width-(x&7),hi,lo;uint16_t mask=((1u<<width)-1)<<shift;
 bits<<=shift;hi=mask>>8;lo=mask;
 hud_pixels[off]=(hud_pixels[off]&~hi)|(bits>>8);hud_pixels[off+1]=(hud_pixels[off+1]&~hi)|(bits>>8);
 if(lo){hud_pixels[off+16]=(hud_pixels[off+16]&~lo)|(uint8_t)bits;hud_pixels[off+17]=(hud_pixels[off+17]&~lo)|(uint8_t)bits;}
 hud_dirty[y>>3]=1;
}
void hud_clear_status(void){uint8_t y,x;for(y=86;y<93;y++)for(x=0;x<6;x++){
 uint16_t o=((uint16_t)(y>>3)*6+x)*16+((y&7)<<1);hud_pixels[o]=0;hud_pixels[o+1]=0;hud_dirty[y>>3]=1;}}
void hud_text(uint8_t x,uint8_t y,const char *s){uint8_t j;while(*s){
 const uint8_t *g=pixel_font+glyph(*s++)*7;
 for(j=0;j<7;j++)hud_bits(x,y+j,5,g[j]);x+=5;
}}
uint8_t score_glyph[5],record_glyph[5];
void hud_score_digit(uint8_t pos,uint8_t d){uint8_t y,g;uint16_t o=96+(uint16_t)pos*16;const uint8_t *rows=big_font+d*8;
 for(y=0;y<8;y++,o+=2){g=rows[y];
  hud_pixels[o]=(hud_pixels[o]&0xf0)|(g>>3);hud_pixels[o+1]=(hud_pixels[o+1]&0xf0)|(g>>3);
  hud_pixels[o+16]=(hud_pixels[o+16]&0x1f)|(g<<5);hud_pixels[o+17]=(hud_pixels[o+17]&0x1f)|(g<<5);
 }hud_dirty[1]=1;
}
void hud_record_digit(uint8_t pos,uint8_t d){const uint16_t offsets[5]={228,244,244,260,260};uint8_t y,g;uint16_t o=offsets[pos];const uint8_t *rows=tiny_digits+d*5;
 for(y=0;y<5;y++,o+=2){g=rows[y];if(pos&1){hud_pixels[o]=(hud_pixels[o]&0xe3)|(g<<2);hud_pixels[o+1]=(hud_pixels[o+1]&0xe3)|(g<<2);}
 else{hud_pixels[o]=(hud_pixels[o]&0xfe)|(g>>2);hud_pixels[o+1]=(hud_pixels[o+1]&0xfe)|(g>>2);hud_pixels[o+16]=(hud_pixels[o+16]&0x3f)|(g<<6);hud_pixels[o+17]=(hud_pixels[o+17]&0x3f)|(g<<6);}
 }hud_dirty[2]=1;
}
const uint32_t hud_powers[5]={1,10,100,1000,10000};
void hud_number(uint8_t x,uint8_t y,uint32_t v,uint8_t n,uint8_t big){
 uint8_t j,d,pos=0,w=big?8:4,h=big?8:5;const uint8_t *g;
 while(n){n--;d=0;while(v>=hud_powers[n]){v-=hud_powers[n];d++;}
 if(y==8){if(score_glyph[pos]!=d){hud_score_digit(pos,d);score_glyph[pos]=d;}pos++;continue;}
 if(y==18){if(record_glyph[pos]!=d){hud_record_digit(pos,d);record_glyph[pos]=d;}pos++;continue;}
 g=big?big_font+d*8:tiny_digits+d*5;
 for(j=0;j<h;j++)hud_bits(x,y+j,w-1,g[j]);x+=w;
 }}
void hud_flush(void){uint8_t i,r;for(i=0;i<18;i++){r=hud_cursor;if(++hud_cursor==18)hud_cursor=0;
 if(hud_dirty[r]){set_bkg_data(128+r*6,6,hud_pixels+(uint16_t)r*96);hud_dirty[r]=0;return;}
 }}
void hud_flush_all(void){uint8_t i;for(i=0;i<18;i++)hud_flush();}
void hud_setup(void){uint8_t i,j;unpack(sidebar_data_rle,hud_pixels,sizeof(hud_pixels));
 set_bkg_data(128,108,hud_pixels);
 for(j=0;j<18;j++){for(i=0;i<6;i++)tmp[i]=128+j*6+i;set_win_tiles(0,j,6,1,tmp);}
 for(i=0;i<5;i++){score_glyph[i]=255;record_glyph[i]=255;}move_win(119,0);hud_valid=1;hud_score=0xffffffffUL;hud_record=0xffffffffUL;hud_lives=255;hud_phase=255;hud_wave=255;hud_shield=255;hud_meter=255;hud_cursor=0;for(i=0;i<18;i++)hud_dirty[i]=0;SHOW_WIN;
}
void update_hud(void){uint8_t j,k,meter;uint16_t row;
 meter=shield_state==0?8:(shield_state==1?0:(358-shield_timer)/45);
 if(meter>8)meter=8;
 if(hud_valid && hud_score==score && hud_record==record && hud_lives==lives && hud_phase==phase && hud_wave==wave && hud_shield==shield_state && hud_meter==meter)return;
 if(hud_score!=score){hud_number(4,8,score,5,1);hud_score=score;return;}
 if(hud_record!=record){hud_number(23,18,record,5,0);hud_record=record;return;}
 if(!hud_valid || hud_lives!=lives){
  for(k=0;k<3;k++){
   const uint8_t *f=face_rows+(k<lives?(lives==1?22:0):44);
   for(j=0;j<11;j++){row=((uint16_t)f[j*2]<<8)|f[j*2+1];hud_bits(5+k*14,44+j,11,row);}
  }
 }
 if(hud_lives!=lives){hud_lives=lives;return;}
 if(!hud_valid || hud_meter!=meter){for(k=0;k<8;k++)for(j=0;j<6;j++)hud_bits(4+k*5,76+j,4,(k<meter||j==0||j==5)?15:9);}
 if(hud_meter!=meter){hud_meter=meter;return;}
 if(!hud_valid || hud_shield!=shield_state){hud_clear_status();hud_text(shield_state==0?11:(shield_state==1?9:4),86,shield_state==0?"LISTO":(shield_state==1?"ACTIVO":"CARGANDO"));}
 if(hud_shield!=shield_state){hud_shield=shield_state;return;}
 if(hud_phase!=phase){hud_number(16,110,phase,2,1);hud_phase=phase;return;}
 if(hud_wave!=wave){hud_number(20,134,wave,1,1);hud_wave=wave;return;}
 hud_score=score;hud_record=record;hud_lives=lives;hud_phase=phase;hud_wave=wave;hud_shield=shield_state;hud_meter=meter;hud_valid=1;
}
