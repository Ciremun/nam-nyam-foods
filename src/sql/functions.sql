CREATE OR REPLACE FUNCTION addUser(uName text, dName text, pass text, uType text, regDate date)
    RETURNS VOID AS $$
    DECLARE newid users.id%TYPE;
    BEGIN
        INSERT INTO users(username, displayname, password, usertype, date)
            VALUES (uName, dName, pass, uType, regDate) RETURNING id INTO newid;
        INSERT INTO cart(user_id) VALUES (newid);

    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION addCartProduct(cID int, pID int, pAmount int)
    RETURNS VOID AS $$
    BEGIN
        IF (SELECT EXISTS(SELECT 1 FROM cartproduct WHERE cart_id = cID AND product_id = pID)) THEN
            UPDATE cartproduct SET amount = amount + pAmount WHERE cart_id = cID AND product_id = pID;
        ELSE
            INSERT INTO cartproduct(cart_id, product_id, amount) VALUES (cID, pID, pAmount);
        END IF;
    END;
    $$ LANGUAGE plpgsql;