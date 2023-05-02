
#define LPAREN ( 
#define RPAREN ) 
#define F(x, y) x + y 
#define ELLIP_FUNC(args...) args 

/proc/F(a,b)
    return a + b

/proc/main()
    LOG( ELLIP_FUNC(F, LPAREN, 'a', 'b', RPAREN) )
    LOG( ELLIP_FUNC(F LPAREN 'a', 'b' RPAREN) )