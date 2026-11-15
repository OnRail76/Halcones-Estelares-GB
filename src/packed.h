/* PackBits only for cold art. No decompression in the combat update path. */
void unpack(const uint8_t *src,uint8_t *dest,uint16_t len){uint8_t n,b;while(len){
 n=*src++;b=n&127;n&=128;b++;len-=b;
 if(n){n=*src++;while(b--)*dest++=n;}else while(b--)*dest++=*src++;
}}
void packed_tiles(const uint8_t *src,uint8_t first,uint8_t count,uint8_t sprite){
 uint8_t tile[16],i=0,n,b,v;uint16_t len=(uint16_t)count*16;
 while(len){n=*src++;b=(n&127)+1;n&=128;v=n?*src++:0;
  while(b--){tile[i++]=n?v:*src++;len--;if(i==16){
   if(sprite)set_sprite_data(first,1,tile);else set_bkg_data(first,1,tile);first++;i=0;
  }}
 }
}

/* Reuse the HUD alphabet: reconstruct identical 8x8 font tiles at scene load. */
void load_font(uint8_t first){uint8_t tile[16],i,y,b;const uint8_t *src=pixel_font;
 tile[14]=0;tile[15]=0;
 for(i=0;i<FONT_COUNT;i++){for(y=0;y<7;y++){b=*src++<<2;tile[y*2]=b;tile[y*2+1]=b;}set_bkg_data(first++,1,tile);}
}
