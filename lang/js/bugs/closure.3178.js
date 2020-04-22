class foo{
  constructor(x) {this.x = x;}
  async bar(y = this.x) {(y!==false)&&console.log('blah');}
}
(async () => await new foo(true).bar())();
