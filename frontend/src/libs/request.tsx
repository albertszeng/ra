import { Game } from './game';
import { WarningLevel } from '../common';

type Visibility = 'PUBLIC' | 'PRIVATE';
type Status = 'WAITING' | 'ONGOING' | 'FINISHED';

type ActionRequest = {
  gameId: string;
  command: string;
};
type ActionResponse = {
  gameAsStr: string;
  gameState: Game;
  // The action performed.
  action: string;
  // Ther user (possibly an AI) that performed it.
  username: string;
};

const AILevels = ['EASY', 'MEDIUM', 'HARD'] as const;
type AILevel = typeof AILevels[number];
type StartRequest = {
  // The number of *human* players.
  numPlayers: number;
  // The number of *AI* players.
  numAIPlayers: number;
  AILevel: AILevel;
  visibility: Visibility;
};
type JoinLeaveRequest = {
  gameId: string;
};
type StartResponse = ActionResponse & JoinLeaveRequest;

type MessageResponse = {
  level: WarningLevel;
  message: string;
};
type ApiResponse = StartResponse & MessageResponse;

type LoginOrRegisterRequest = {
  username: string;
  password: string;
};
type TokenLoginRequest = {
  token: string;
};
type LoginResponse = {
  level: WarningLevel;
  message: string;
  token?: string;
  username?: string;
};
type LoginSuccess = {
  token: string;
  username: string;
};

type ListGame = {
  id: string;
  players?: string[];
  visibility?: Visibility;
  status?: Status;
  numPlayers?: number;
  deleted?: boolean;
};
type ValidatedListGame = {
  id: string;
  players: string[];
  status: Status;
  visibility: Visibility;
  numPlayers: number;
};
type ListGamesResponse = {
  partial: boolean;
  games: ListGame[];
};

type DeleteRequest = {
  gameId: string;
};

type AddPlayerRequest = {
  gameId: string;
};

export { AILevels };

export type {
  ActionRequest,
  AddPlayerRequest,
  AILevel,
  ApiResponse,
  DeleteRequest,
  JoinLeaveRequest,
  ListGame,
  ListGamesResponse,
  LoginOrRegisterRequest,
  LoginResponse,
  LoginSuccess,
  MessageResponse,
  StartRequest,
  StartResponse,
  TokenLoginRequest,
  ValidatedListGame,
  Visibility,
  WarningLevel,
};
