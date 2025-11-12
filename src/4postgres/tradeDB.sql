--
-- PostgreSQL database dump
--

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 17.0

-- Started on 2025-11-12 14:09:08 MST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: sultanalzoghaibi
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO sultanalzoghaibi;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 210 (class 1259 OID 40962)
-- Name: trades; Type: TABLE; Schema: public; Owner: sultanalzoghaibi
--

CREATE TABLE public.trades (
    id integer NOT NULL,
    symbol text,
    trade_time bigint,
    price numeric,
    quantity numeric,
    stream text,
    inserted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.trades OWNER TO sultanalzoghaibi;

--
-- TOC entry 209 (class 1259 OID 40961)
-- Name: trades_id_seq; Type: SEQUENCE; Schema: public; Owner: sultanalzoghaibi
--

CREATE SEQUENCE public.trades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trades_id_seq OWNER TO sultanalzoghaibi;

--
-- TOC entry 3786 (class 0 OID 0)
-- Dependencies: 209
-- Name: trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sultanalzoghaibi
--

ALTER SEQUENCE public.trades_id_seq OWNED BY public.trades.id;


--
-- TOC entry 3635 (class 2604 OID 40965)
-- Name: trades id; Type: DEFAULT; Schema: public; Owner: sultanalzoghaibi
--

ALTER TABLE ONLY public.trades ALTER COLUMN id SET DEFAULT nextval('public.trades_id_seq'::regclass);


--
-- TOC entry 3779 (class 0 OID 40962)
-- Dependencies: 210
-- Data for Name: trades; Type: TABLE DATA; Schema: public; Owner: sultanalzoghaibi
--

COPY public.trades (id, symbol, trade_time, price, quantity, stream, inserted_at) FROM stdin;
1	ETHUSDT	1762979951735	3424.84000000	0.00160000	ethusdt@trade	2025-11-12 13:05:08.841949
2	ETHUSDT	1762979951735	3424.84000000	0.00160000	ethusdt@trade	2025-11-12 13:05:08.84538
3	ETHUSDT	1762979951735	3424.84000000	0.00160000	ethusdt@trade	2025-11-12 13:05:08.845951
4	BTCUSDT	1762979951733	101629.99000000	0.00007000	btcusdt@trade	2025-11-12 13:05:08.846536
5	BTCUSDT	1762979951733	101629.99000000	0.00007000	btcusdt@trade	2025-11-12 13:05:08.847042
6	BTCUSDT	1762979951733	101629.99000000	0.00007000	btcusdt@trade	2025-11-12 13:05:08.847829
7	BTCUSDT	1762979951733	101629.99000000	0.00007000	btcusdt@trade	2025-11-12 13:05:40.089589
8	ETHUSDT	1762979951735	3424.84000000	0.00160000	ethusdt@trade	2025-11-12 13:05:40.090649
\.


--
-- TOC entry 3787 (class 0 OID 0)
-- Dependencies: 209
-- Name: trades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sultanalzoghaibi
--

SELECT pg_catalog.setval('public.trades_id_seq', 8, true);


--
-- TOC entry 3638 (class 2606 OID 40970)
-- Name: trades trades_pkey; Type: CONSTRAINT; Schema: public; Owner: sultanalzoghaibi
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_pkey PRIMARY KEY (id);


--
-- TOC entry 3785 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: sultanalzoghaibi
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2025-11-12 14:09:08 MST

--
-- PostgreSQL database dump complete
--

